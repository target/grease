from abc import ABCMeta, abstractmethod
from tgt_grease.core import Logging, GreaseContainer


class Command(object):
    """Abstract class for commands in GREASE

    Attributes:
        __metaclass__ (ABCMeta): Metadata class object
        purpose (str): The purpose of the command
        ioc (GreaseContainer): IOC container for access to system resources

    """

    __metaclass__ = ABCMeta
    purpose = "Stuff"
    ioc = None

    def __init__(self, Logger=None):
        if Logging and isinstance(Logger, Logging):
            self.ioc = GreaseContainer(Logger)
        else:
            self.ioc = GreaseContainer()

    @abstractmethod
    def execute(self, context):
        """Base Execute Method

        Args:
            context (dict): context for the command to use

        Returns:
            bool: Command Success

        """
        pass
