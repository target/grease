from tgt_grease.core.Types import Command
from tgt_grease.enterprise.Model import Scan


class Scanner(Command):
    """The Scan Command

    This class is the ingestion of information for GREASE. It utilizes configurations to 'wire' scanners together

    """

    __author__ = "James E. Bell Jr."
    __version__ = "2.0.0"
    purpose = "Parse the configured environment for data and schedule de-duplicated data for detection"
    help = """
    This command scans the environment via the node configuration. This enables GREASE to 'see' its' environment and 
    schedule jobs a detection node
    
    Args:
        --loop:<int>
            How many scans you would like to go through
        --config:<filename>
            The specific config file you want to parse
        --source:<source>
            The specific source to parse all configs of
        --foreground
            Print Log messages to foreground
    """

    def __init__(self):
        super(Scanner, self).__init__()

    def execute(self, context):
        """Execute method of the scanner prototype

        Args:
            context (dict): Command Context

        Note:
            This method normally will *never* return. As it is a prototype. So it should continue into infinity

        Returns:
             bool: True always unless failures occur

        """
        if context.get('foreground'):
            # set foreground if in context
            self.ioc.getLogger().foreground = True
        self.ioc.getLogger().trace("Scanner starting", trace=True)
        scanner = Scan(self.ioc)
        # create Parse Args
        args = {
            'source': context.get('source', self.ioc.getConfig().get('Sourcing', 'source', None)),
            'config': context.get('config', self.ioc.getConfig().get('Sourcing', 'config', None))
        }
        if 'loop' in context:
            # scan only a certain amount of times
            scan_count = 0
            while scan_count < int(context.get('loop')):
                scanner.Parse(**args)
                scan_count += 1
        else:
            try:
                while True:
                    scanner.Parse(**args)
            except KeyboardInterrupt:
                # graceful close for scanning
                self.ioc.getLogger().trace("Keyboard interrupt in scanner detected", trace=True)
                return True
        # ensure we clean up after ourselves
        if context.get('foreground'):
            self.ioc.getLogger().foreground = False
        return True
