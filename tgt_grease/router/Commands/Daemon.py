from logging import DEBUG
from tgt_grease.core import GreaseContainer


class DaemonProcess(object):
    """Actual daemon processing for GREASE Daemon

    Attributes:
        ioc (GreaseContainer): The Grease IOC

    """

    ioc = None

    def __init__(self, ioc):
        if isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()

    def log_once_per_second(self, message, level=DEBUG):
        """Log Message once per second

        Args:
            message (str): Message to log
            level (int): Log Level

        Returns:
            None: Void Method to fire log message

        """
        self.ioc.getLogger().TriageMessage(message=message, level=level)

    def server(self):
        """Server process for ensuring prototypes & jobs are running"""
        return True
