from .Command import Command
import datetime
from abc import ABCMeta, abstractmethod
from bson.objectid import ObjectId
from tgt_grease.enterprise.Model import Deduplication


class ScheduledCommand(Command):
    """Scheduled Commands Run as Prototypes

    This type is used for commands that need to be run cyclically. They will be run as prototypes (always running).
    Make sure to fill out the **timeToRun** and **run** methods

    """

    __metaclass__ = ABCMeta

    def __init__(self, logger=None):
        super(ScheduledCommand, self).__init__(logger)

    @abstractmethod
    def timeToRun(self):
        """Checks to ensure it is time to run

        Returns:
            bool: If time to run then true else false

        """
        pass

    @abstractmethod
    def run(self):
        """Put your code here to run whenever the conditions in timeToRun are defined

        Note:
            We recommend returning something valuable since the engine logs the result of the method in verbose mode

        """
        pass

    def execute(self, context):
        """Command execute method

        This will run continuously waiting for `timeToRun` to return true to call `run`

        Args:
            context (dict): context for the command to use **Not Used Here**

        """
        while True:
            if self.timeToRun():
                result = self.run()
                self.ioc.getLogger().debug(
                    "Scheduled command result of [{0}] was [{1}]".format(
                        self.__class__.__name__,
                        result
                    ), verbose=True
                )
                self.ioc.getLogger().info("Scheduled Command [{0}] has executed".format(self.__class__.__name__))
                self.ioc.getCollection('SourceData').insert_one({
                    'grease_data': {
                        'sourcing': {
                            'server': ObjectId(self.ioc.getConfig().NodeIdentity)
                        },
                        'detection': {
                            'server': ObjectId(self.ioc.getConfig().NodeIdentity),
                            'start': datetime.datetime.utcnow(),
                            'end': datetime.datetime.utcnow(),
                            'detection': {}
                        },
                        'scheduling': {
                            'server': ObjectId(self.ioc.getConfig().NodeIdentity),
                            'start': datetime.datetime.utcnow(),
                            'end': datetime.datetime.utcnow()
                        },
                        'execution': {
                            'server': ObjectId(self.ioc.getConfig().NodeIdentity),
                            'assignmentTime': datetime.datetime.utcnow(),
                            'completeTime': datetime.datetime.utcnow(),
                            'returnData': {},
                            'executionSuccess': True,
                            'commandSuccess': True,
                            'failures': 0
                        }
                    },
                    'source': 'grease_internal_scheduled_job_{0}'.format(self.__class__.__name__),
                    'configuration': None,
                    'data': {},
                    'createTime': datetime.datetime.utcnow(),
                    'expiry': Deduplication.generate_max_expiry_time(1)
                })
            else:
                self.ioc.getLogger().trace(
                    "Scheduled Job not scheduled to run [{0}]".format(self.__class__.__name__),
                    trace=True
                )
                continue
