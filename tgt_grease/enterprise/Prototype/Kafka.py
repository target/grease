from tgt_grease.core.Types import Command
from tgt_grease.enterprise.Model import KafkaSource


class Kafka(Command):
    """The Kafka Command

    This class is the ingestion of Kafka topics for GREASE. 

    """

    __author__ = "Ronald Queensen, Dustin Gundrum"
    __version__ = "1.0.0"
    purpose = "Listen to the configured Kafka topics and send the chosen keys to detection"
    help = """
    This command spins up a KafkaConsumer object, and runs KafkaSource.run, which will load all the kafka configs and begin consuming messages.
    
    Args:
        --config:<filename>
            The specific config file you want to parse
        --foreground
            Print Log messages to foreground
    """

    def __init__(self):
        super(Kafka, self).__init__()

    def execute(self, context):
        """Execute method of the Kafka prototype

        Args:
            context (dict): Command Context

        Note:
            This method normally will *never* return, as it is a prototype. It should continue indefinitely

        Returns:
             bool: True iff no failures occur, otherwise False

        """
        if context.get('foreground'):
            # set foreground if in context
            self.ioc.getLogger().foreground = True
        self.ioc.getLogger().trace("Kafka starting", trace=True)

        kafka_source = KafkaSource(self.ioc)
        try:
            kafka_source.run(context.get("config"))
        except KeyboardInterrupt:
            # graceful close for scanning
            self.ioc.getLogger().trace("Keyboard interrupt in scanner detected", trace=True)
            return True
        # ensure we clean up after ourselves
        if context.get('foreground'):
            self.ioc.getLogger().foreground = False
        return False
