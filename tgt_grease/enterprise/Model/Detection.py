from tgt_grease.core import GreaseContainer
from tgt_grease.core import ImportTool
from bson.objectid import ObjectId
import pymongo


class Detect(object):
    """Detection class for GREASE detect

    This is the model to actually utilize the detectors to parse the sources from scan

    Attributes:
        ioc (GreaseContainer): IOC for scanning
        impTool (ImportTool): Import Utility Instance

    """

    def __init__(self, ioc=None):
        if ioc and isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()
        self.impTool = ImportTool(self.ioc.getLogger())
        self.ioc.ensureRegistration()

    def detectSource(self):
        """This will perform detection the oldest source from SourceData

        Returns:
            bool: If detection process was successful

        """

    def getScheduledSource(self):
        """Queries for oldest source that has been assigned for detection

        Returns:
            dict: source awaiting detection

        """
        return self.ioc.getCollection('SourceData').find_one(
            {
                'grease_data.detection.server': ObjectId(self.ioc.getConfig().NodeIdentity),
                'grease_data.detection.detectionStart': None,
                'grease_data.detection.detectionEnd': None,
            },
            sort=[('grease_data.createTime', pymongo.DESCENDING)]
        )
