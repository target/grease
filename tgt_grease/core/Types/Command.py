from abc import ABCMeta, abstractmethod
from tgt_grease.core import Logging, GreaseContainer
from datetime import datetime


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
    start_time = None
    exec_data = {'execVal': False, 'retVal': False, 'retData': {}}

    def __init__(self, Logger=None):
        if Logging and isinstance(Logger, Logging):
            self.ioc = GreaseContainer(Logger)
        else:
            self.ioc = GreaseContainer()
        self.variable_storage = self.ioc.getMongo()\
            .Client()\
            .get_database(self.ioc.getConfig().get('Connectivity', 'MongoDB').get('db', 'grease'))\
            .get_collection(self.__class__.__name__)
        self.start_time = datetime.utcnow()

    def getExecVal(self):
        """Get the execution attempt success

        Returns:
            bool: If the command executed without exception

        """
        return self.exec_data.get('execVal', False)

    def getRetVal(self):
        """Get the execution boolean return state

        Returns:
            bool: the boolean return value of execute

        """
        return self.exec_data.get('retVal', False)

    def getRetData(self):
        """Get any data the execute method wanted to put into telemetry

        Returns:
            dict: The Key/Value pairs from the execute method execution

        """
        return self.exec_data.get('retData', {})

    def setRetData(self, Key, Data):
        """Put Data into the retData object to be inserted into telemetry

        Args:
            Key (str): Key for the data to be stored
            Data (object): JSON-able object to store

        Returns:
            None: Void Method to put data

        """
        self.exec_data['retData'][Key] = Data

    def __del__(self):
        # close mongo connection
        self.ioc.getMongo().Close()
        del self.variable_storage

    def safe_execute(self, context):
        return bool(self.execute(context))

    @abstractmethod
    def execute(self, context):
        """Base Execute Method

        Args:
            context (dict): context for the command to use

        Returns:
            bool: Command Success

        """
        pass
