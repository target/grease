from abc import ABCMeta, abstractmethod
from tgt_grease.core import Logging, GreaseContainer
from datetime import datetime
from tgt_grease.core.Decorators import grease_log
import sys
import os
import traceback


class Command(object):
    """Abstract class for commands in GREASE

    Attributes:
        __metaclass__ (ABCMeta): Metadata class object
        purpose (str): The purpose of the command
        help (str): Help string for the command line
        __author__ (str): Authorship string
        __version__ (str): Command Version
        os_needed (str): If a specific OS is needed then set this
        ioc (GreaseContainer): IOC container for access to system resources
        variable_storage (pymongo.collection): collection object for command

    """

    ###
    # Command Metadata information
    ###
    purpose = "Default"
    help = """
    No Help Information Provided
    """
    __author__ = "Jimmy The Programmer"
    __version__ = "1.0.0"
    os_needed = None
    __metaclass__ = ABCMeta

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
        self.exec_data = {'execVal': False, 'retVal': False, 'data': {}}
        self.__failures = 0

    @property
    def failures(self):
        return self.__failures

    @failures.setter
    def failures(self, val):
        self.__failures = val

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

    def getData(self):
        """Get any data the execute method wanted to put into telemetry

        Returns:
            dict: The Key/Value pairs from the execute method execution

        """
        return self.exec_data.get('data', {})

    def setData(self, Key, Data):
        """Put Data into the data object to be inserted into telemetry

        Args:
            Key (str): Key for the data to be stored
            Data (object): JSON-able object to store

        Returns:
            None: Void Method to put data

        """
        self.exec_data['data'][Key] = Data

    def __del__(self):
        # close mongo connection
        self.ioc.getMongo().Close()

    @grease_log
    def safe_execute(self, context=None):
        """Attempt execution and prevent MOST exceptions

        Args:
            context (dict): context for the command to use

        Returns:
            None: Void method to attempt exceptions

        """
        if not context:
            context = {}
        try:
            try:
                self.exec_data['execVal'] = True
                self.exec_data['retVal'] = bool(self.execute(context))
            except BaseException:
                self.exec_data['execVal'] = False
                exc_type, exc_obj, exc_tb = sys.exc_info()
                tb = traceback.format_exception(exc_type, exc_obj, exc_tb)
                self.ioc.getLogger().error(
                    "Failed to execute [{0}] execute got exception!".format(self.__class__.__name__),
                    additional={
                        'file': os.path.split(str(str(tb[2]).split('"')[1]))[1],
                        'type': str(exc_type),
                        'line': str(str(tb[2]).split(",")[1]).split(' ')[2]
                    }
                )
            except:
                self.ioc.getLogger().error(
                    "Failed to execute [{0}] execute got exception!".format(self.__class__.__name__),
                )
        except:
            self.ioc.getLogger().error(
                "Failed to execute [{0}] execute major exception".format(self.__class__.__name__),
            )

    @abstractmethod
    def execute(self, context):
        """Base Execute Method

        This method should *always* be overridden in child classes. This is the code that will run when your command
        is called. If this method is not implemented then the class will fail loading.

        Args:
            context (dict): context for the command to use

        Returns:
            bool: Command Success

        """
        pass

    def prevent_retries(self):
        """
        Sets a flag in the command's return data that will signal to stop retrying, even before the default
        retry limit is met.

        """
        self.setData("no_retry", True)

