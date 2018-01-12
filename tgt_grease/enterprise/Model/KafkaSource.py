from tgt_grease.core import GreaseContainer
from .Configuration import PrototypeConfig
from tgt_grease.core import ImportTool
from .CentralScheduling import Scheduling
import multiprocessing as mp
from time import time

MIN_BACKLOG = 5
MAX_BACKLOG = 20
SLEEP_TIME = 5

class KafkaSource(object):

    def __init__(self, ioc=None):
        if ioc and isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()
        self.conf = PrototypeConfig(self.ioc)
        self.impTool = ImportTool(self.ioc.getLogger())
        self.scheduler = Scheduling(self.ioc)
        self.configs = []

    def run(self, config=None):
        if config:
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
        monitor_consumer = KafkaSource.make_consumer(ioc, config)

        procs = []
        procs.append(KafkaSource.create_consumer_proc(ioc, config))

        while procs:
            KafkaSource.reallocate_consumers(ioc, config, monitor_consumer, procs)
            KafkaSource.sleep(SLEEP_TIME)
            procs = list(filter(lambda x: x.is_alive(), procs))

        return False

    @staticmethod
    def create_consumer_proc(ioc, config):
        parent_conn, child_conn = mp.Pipe()
        proc = mp.Process(target=KafkaSource.consume, args=(ioc, config, child_conn,))
        proc.daemon = True
        proc.start()
        KafkaSource.sleep(SLEEP_TIME)
        return proc, parent_conn

    @staticmethod
    def consume(ioc, config, pipe):
        consumer = KafkaSource.make_consumer(ioc, config)
        for msg in consumer:
            if not pipe.empty():
                return
            message_dict = KafkaSource.transform_message(ioc, config, msg)
            if message_dict:
                KafkaSource.send_to_scheduling(ioc, config, message_dict)

    @staticmethod
    def sleep(sleep_sec):
        wake_time = time() + sleep_sec
        while time() < wake_time:
            continue

    @staticmethod
    def make_consumer(ioc, config):
        return []

    @staticmethod
    def transform_message(ioc, config, message):
        return True

    @staticmethod
    def reallocate_consumers(ioc, config, monitor_consumer, procs):
        backlog1 = KafkaSource.get_backlog(monitor_consumer)
        KafkaSource.sleep(SLEEP_TIME)
        backlog2 = KafkaSource.get_backlog(monitor_consumer)

        if backlog1 > MAX_BACKLOG and backlog2 > MAX_BACKLOG:
            procs.append(KafkaSource.create_consumer_proc(ioc, config))
        elif backlog1 <= MIN_BACKLOG and backlog2 <= MIN_BACKLOG and len(procs) > 1:
            procs[0][1].send("STOP")

    @staticmethod
    def get_backlog(monitor_consumer):
        return True

    @staticmethod
    def send_to_scheduling(ioc, config, message):
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
        return []
