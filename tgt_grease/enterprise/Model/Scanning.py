from tgt_grease.core import GreaseContainer
from .Configuration import PrototypeConfig


class Scan(object):
    """Scanning class for GREASE Scanner

    This is the model to actually utilize the scanners to parse the configured environments

    Attributes:
        ioc (GreaseContainer): IOC for scanning
        conf (PrototypeConfig): Prototype configuration instance

    """

    def __init__(self, ioc=None):
        if ioc and isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()
        self.conf = PrototypeConfig(self.ioc)

    def Parse(self, source=None, config=None):
        """This will read all configurations and attempt to scan the environment

        This is the primary business logic for scanning in GREASE. This method will use configurations to parse
        the environment and attempt to schedule

        Args:
            source (str): If set will only parse for the source listed
            config (str): If set will only parse the specified config

        Returns:
            bool: True unless error

        """
        self.ioc.getLogger().trace("Starting Parse of Environment", trace=True)
        return True
