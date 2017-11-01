from abc import ABCMeta, abstractmethod
from tgt_grease.core import Logging, GreaseContainer


class Command(object):
    """Abstract class for commands in GREASE

    Attributes:
        __metaclass__ (ABCMeta): Metadata class object
        purpose (str): The purpose of the command
        ioc (GreaseContainer): IOC container for access to system resources
        variable_storage (pymongo.collection): collection object for command

    """

    __metaclass__ = ABCMeta
    purpose = "Stuff"
    ioc = None
    variable_storage = None

    def __init__(self, Logger=None):
        if Logging and isinstance(Logger, Logging):
            self.ioc = GreaseContainer(Logger)
        else:
            self.ioc = GreaseContainer()
        self.variable_storage = self.ioc.getMongo()\
            .Client()\
            .get_database(self.ioc.getConfig().get('Connectivity', 'MongoDB').get('db', 'grease'))\
            .get_collection(self.__class__.__name__)

    def __del__(self):
        # close mongo connection
        self.ioc.getMongo().Close()
        del self.variable_storage

    @abstractmethod
    def execute(self, context):
        """Base Execute Method

        Args:
            context (dict): context for the command to use

        Returns:
            bool: Command Success

        """
        pass
