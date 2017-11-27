from tgt_grease.core import GreaseContainer, ImportTool
from .Configuration import PrototypeConfig
from .CentralScheduling import Scheduling
from bson.objectid import ObjectId
import pymongo


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
        pass

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
