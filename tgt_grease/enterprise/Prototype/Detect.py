from tgt_grease.core.Types import Command
from tgt_grease.enterprise.Model import Detect


class Detection(Command):
    """The detect command

    This class is the source detection for GREASE. It utilizes the logic block of your configurations to determine
    if a job needs to be run

    """

    __author__ = "James E. Bell Jr."
    __version__ = "2.0.0"
    purpose = "Detect sources from scan and schedule them for job scheduling"
    help = """
    This command detects possible jobs from the scan command
    
    Args:
        --loop:<int>
            How many detection cycles to do
        --foreground
            Print log messages to the foreground
    """

    def execute(self, context):
        """Execute method of the detection prototype

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
        Detector = Detect(self.ioc)
        if 'loop' in context:
            # scan only a certain amount of times
            scan_count = 0
            while scan_count < int(context.get('loop')):
                if not Detector.detectSource():
                    self.ioc.getLogger().warning("Detection Process Failed", notify=False)
                scan_count += 1
        else:
            try:
                while True:
                    if not Detector.detectSource():
                        self.ioc.getLogger().warning("Detection Process Failed", notify=False)
                    continue
            except KeyboardInterrupt:
                # graceful close for scanning
                self.ioc.getLogger().trace("Keyboard interrupt in detect detected", trace=True)
                return True
        # ensure we clean up after ourselves
        if context.get('foreground'):
            self.ioc.getLogger().foreground = False
        return True
