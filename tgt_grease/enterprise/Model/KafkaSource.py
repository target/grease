from tgt_grease.core import GreaseContainer
from .Configuration import PrototypeConfig
from tgt_grease.core import ImportTool
from .CentralScheduling import Scheduling
from .DeDuplication import Deduplication
import multiprocessing as mp
from time import time
import kafka

MIN_BACKLOG = 5     # If the Kafka message backlog falls below this number, we will kill a consumer
MAX_BACKLOG = 20    # If the Kafka message backlog rises above this number, we will make a consumer
SLEEP_TIME = 5      # Sleep this many seconds after creating a consumer (to wait for initialization) and between reallocating consumers

class KafkaSource(object):
    """Kafka class for sourcing Kafka messages

    This Source will create and dynamically scale the number of Kafka consumers for the topics specified in the Config, and 
    then sends the parsed messages (containing only the keys/values specified in the Config) to Scheduling.

    Attributes:
        ioc (GreaseContainer): IOC for scanning
        conf (PrototypeConfig): Prototype configuration instance
        impTool (ImportTool): Import Utility Instance
        dedup (Deduplication): Deduplication instance to be used
        configs (List[dict]): List of Kafka Configs

    """

    def __init__(self, ioc=None):
        if ioc and isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()
        self.conf = PrototypeConfig(self.ioc)
        self.impTool = ImportTool(self.ioc.getLogger())
        self.scheduler = Scheduling(self.ioc)
        self.dedup = Deduplication(self.ioc)
        self.configs = []

    def run(self, config=None):
        """This will load all Kafka configs (unless a specific one is provided) and spin up consumer processes for all of them.

        It should never return anything unless something goes wrong with Kafka consumption.

        Creates a process for each Kafka config to begin parsing messages. This parent process then monitors its children, 
        and prunes dead processes. Once all children are dead, we return False.

        Note:
            If a configuration is set then *only* that configuration is parsed. If both are provided then the configuration
            will *only* be parsed if it is of the source provided.

        Args:
            config (dict): If set will only parse the specified config

        Returns:
            bool: False if an error occurs, else never returns

        """
        if config:
            if config.get('source') != 'kafka':
                self.ioc.getLogger().error("Invalid source type: {0} provided to KafkaSource".format(config.get('source', "None")), notify=False)
                return False
            self.configs = [config]
        else:
            self.configs = self.get_configs()

        procs = []
        for conf in self.configs:
            proc = mp.Process(target=KafkaSource.consumer_manager, args=(self.ioc, conf,))
            proc.daemon = False
            proc.start()
            procs.append(proc)

        while procs:
            procs = list(filter(lambda x: x.is_alive(), procs))
        
        return False

    @staticmethod
    def consumer_manager(ioc, config):
        """Creates and reallocates consumer processes within the same consumer group for a single config

        Args:
            ioc (GreaseContainer): Used for logging since we can't use self in procs
            config (dict): Configuration for a Kafka source

        Returns:
            bool: False if all consumers are stopped

        """
        monitor_consumer = KafkaSource.make_consumer(ioc, config)

        procs = []
        procs.append(KafkaSource.create_consumer_proc(ioc, config))

        while procs:
            KafkaSource.reallocate_consumers(ioc, config, monitor_consumer, procs)
            procs = list(filter(lambda x: x.is_alive(), procs))

        return False

    @staticmethod
    def create_consumer_proc(ioc, config):
        """Creates a consumer process, pipe pair for a given config

        Args:
            ioc (GreaseContainer): Used for logging since we can't use self in procs
            config (dict): Configuration for a Kafka source

        Returns:
            multiprocessing.Process: The Process running the Kafka consumer
            multiprocessing.Pipe: The parent end of the Pipe used to send a kill signal to the consumer process

        """
        parent_conn, child_conn = mp.Pipe()
        proc = mp.Process(target=KafkaSource.consume, args=(ioc, config, child_conn,))
        proc.daemon = True
        proc.start()
        return proc, parent_conn

    @staticmethod
    def consume(ioc, config, pipe):
        """The Kafka consumer in charge of parsing messages according to the config, then sends the parsed dict to Scheduling

        Args:
            ioc (GreaseContainer): Used for logging since we can't use self in procs
            config (dict): Configuration for a Kafka source
            pipe (multiprocessing.Pipe): Child end of the pipe used to receive signals from parent process

        Returns:
            bool: False if kill signal is received

        """
        consumer = KafkaSource.make_consumer(ioc, config)

        for msg in consumer:
            if not pipe.empty():    # If the parent sends a signal pipe
                return False
            message_dict = KafkaSource.parse_message(ioc, config, msg)
            if message_dict:
                KafkaSource.send_to_scheduling(ioc, config, message_dict)

    @staticmethod
    def sleep(sleep_sec):
        """Multiprocessing safe sleep function that waits sleep_sec seconds without affecting child processes

        Args:
            sleep_sec (int): Number of seconds to idle

        """
        wake_time = time() + sleep_sec
        while time() < wake_time:
            continue

    @staticmethod
    def make_consumer(ioc, config):
        """Creates a KafkaConsumer object from the params in config

        Args:
            ioc (GreaseContainer): Used for logging since we can't use self in procs
            config (dict): Configuration for a Kafka source

        Returns:
            kafka.KafkaConsumer: KafkaConsumer object initialized with params from config

        """

        KafkaSource.sleep(SLEEP_TIME)   # Gives the consumer time to initialize
        return []

    @staticmethod
    def parse_message(ioc, config, message):
        """Parses a message from Kafka according to the config

        Note:
            transform_message extracts only the keys/values from the message as specified in the config.
            By default, we split the keys by "." - so if you wanted to access the value stored at 
            message[a][b][c], your config would contain the key "a.b.c". You can overwrite the "." key
            splitter explicitly in your Config. These values will be written to their respective alias also 
            specified in the config. 

        Args:
            ioc (GreaseContainer): Used for logging since we can't use self in procs
            config (dict): Configuration for a Kafka source
            message (dict): Individual message received from Kafka topic

        Returns:
            dict: A flat dictionary containing only the keys/values from the message as specified in the config

        """
        return {}

    @staticmethod
    def reallocate_consumers(ioc, config, monitor_consumer, procs):
        """Determines whether to create or kill a consumer based on current message backlog, then performs that action

        Args:
            ioc (GreaseContainer): Used for logging since we can't use self in procs
            config (dict): Configuration for a Kafka source
            monitor_consumer (kafka.KafkaConsumer): KafkaConsumer used solely for measuring message backlog
            procs (list[(multiprocessing.Process, multiprocessing.Pipe)]): List of current consumer process/pipe pairs

        """

        backlog1 = KafkaSource.get_backlog(ioc, monitor_consumer)
        KafkaSource.sleep(SLEEP_TIME)
        backlog2 = KafkaSource.get_backlog(ioc, monitor_consumer)

        if backlog1 > MAX_BACKLOG and backlog2 > MAX_BACKLOG:
            procs.append(KafkaSource.create_consumer_proc(ioc, config))
        elif backlog1 <= MIN_BACKLOG and backlog2 <= MIN_BACKLOG and len(procs) > 1:
            KafkaSource.kill_consumer_proc(ioc, procs[0])

    @staticmethod
    def kill_consumer_proc(ioc, proc_tup):
        """Sends a kill signal to the first proc in the procs array

        Args:
            ioc (GreaseContainer): Used for logging since we can't use self in procs
            proc_tup ((multiprocessing.Process, multiprocessing.Pipe)): Process/Pipe tuple to be killed

        """
        proc_tup[1].send("STOP")
        KafkaSource.sleep(SLEEP_TIME)

    @staticmethod
    def get_backlog(ioc, consumer):
        """Gets the current message backlog for a given consumer

        Args:
            ioc (GreaseContainer): Used for logging since we can't use self in procs
            consumer (kafka.KafkaConsumer)

        Returns:
            int: the number of messages in the backlog

        """
        return True

    @staticmethod
    def send_to_scheduling(ioc, config, message):
        """Sends a parsed message dictionary to scheduling

        Args:
            ioc (GreaseContainer): Used for logging since we can't use self in procs
            config (dict): Configuration for a Kafka source
            message (dict): Individual parsed message received from Kafka topic

        Returns:
            bool: True if scheduling is successful

        """
        scheduler = Scheduling(ioc)
        if not message:
            return False
        if scheduler.scheduleDetection(config.get('source'), config.get('name'), message):
            ioc.getLogger().info(
                "Data scheduled for detection from source [{0}]".format(config.get('source')),
                trace=True
            )
            return True
        else:
            ioc.getLogger().error("Scheduling failed for source document!", notify=False)
            return False

    def get_configs(self):
        """Gets all Configs with the source 'kafka'

        Returns:
            list[dict]: A list of all kafka config dicts

        """
        return []
