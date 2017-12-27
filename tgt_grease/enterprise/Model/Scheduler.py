from tgt_grease.core import GreaseContainer, ImportTool
from .Configuration import PrototypeConfig
from .CentralScheduling import Scheduling
from bson.objectid import ObjectId
import pymongo
import datetime


class Scheduler(object):
    """Job Scheduler Model

    This model will attempt to schedule a job for execution

    Attributes:
        ioc (GreaseContainer): IOC for scanning
        impTool (ImportTool): Import Utility Instance
        conf (PrototypeConfig): Prototype configuration tool
        scheduler (Scheduling): Prototype Scheduling Service Instance

    """

    def __init__(self, ioc=None):
        if ioc and isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()
        self.impTool = ImportTool(self.ioc.getLogger())
        self.ioc.ensureRegistration()
        self.conf = PrototypeConfig(self.ioc)
        self.scheduler = Scheduling(self.ioc)

    def scheduleExecution(self):
        """Schedules the oldest successfully detected source to execution

        Returns:
            bool: True if detection is successful else false

        """
        source = self.getDetectedSource()
        if source:
            self.ioc.getLogger().trace("Attempting schedule of source", trace=True)
            self.ioc.getCollection('SourceData').update_one(
                {'_id': ObjectId(source.get('_id'))},
                {
                    '$set': {
                        'grease_data.scheduling.start': datetime.datetime.utcnow()
                    }
                }
            )
            if self.schedule(source):
                self.ioc.getLogger().trace("Scheduling [{0}] was successful".format(source['_id']), trace=True)
                self.ioc.getCollection('SourceData').update_one(
                    {'_id': ObjectId(source.get('_id'))},
                    {
                        '$set': {
                            'grease_data.scheduling.end': datetime.datetime.utcnow()
                        }
                    }
                )
                return True
            else:
                self.ioc.getLogger().error(
                    "Failed to schedule [{0}] for execution".format(source['_id']),
                    trace=True,
                    notify=False
                )
                self.ioc.getCollection('SourceData').update_one(
                    {'_id': ObjectId(source.get('_id'))},
                    {
                        '$set': {
                            'grease_data.scheduling.start': None,
                            'grease_data.scheduling.end': None
                        }
                    }
                )
                return False
        else:
            self.ioc.getLogger().trace("No sources detected for this node at this time", trace=True)
            return True

    def getDetectedSource(self):
        """Gets the oldest successfully detected source

        Returns:
            dict: Object from MongoDB

        """
        return self.ioc.getCollection('SourceData').find_one(
            {
                    'grease_data.scheduling.server': ObjectId(self.ioc.getConfig().NodeIdentity),
                    'grease_data.scheduling.start': None,
                    'grease_data.scheduling.end': None
            },
            sort=[('grease_data.createTime', pymongo.DESCENDING)]
        )

    def schedule(self, source):
        """Schedules source for execution

        Returns:
            bool: If scheduling was successful or not

        """
        if isinstance(source['configuration'], bytes):
            config = self.conf.get_config(source['configuration'].decode())
        else:
            config = self.conf.get_config(source['configuration'])
        if not config:
            self.ioc.getLogger().error("Failed to load configuration for source [{0}]".format(source['_id']))
            return False
        server, jobs = self.scheduler.determineExecutionServer(config.get('exe_env', 'general'))
        if not server:
            self.ioc.getLogger().error(
                "Failed to find an Execution Node for environment [{0}]".format(config.get('exe_env', 'general'))
            )
            return False
        self.ioc.getCollection('SourceData').update_one(
            {'_id': ObjectId(source['_id'])},
            {
                '$set': {
                    'grease_data.execution.server': ObjectId(server),
                    'grease_data.execution.assignmentTime': datetime.datetime.utcnow(),
                }
            }
        )
        self.ioc.getCollection('JobServer').update_one(
            {'_id': ObjectId(server)},
            {
                '$set': {
                    'jobs': jobs + 1
                }
            }
        )
        return True
