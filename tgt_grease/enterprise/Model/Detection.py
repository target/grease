from tgt_grease.core import GreaseContainer
from tgt_grease.core import ImportTool
from .Configuration import PrototypeConfig
from .CentralScheduling import Scheduling
from .BaseDetector import Detector
from bson.objectid import ObjectId
import pymongo
import datetime


class Detect(object):
    """Detection class for GREASE detect

    This is the model to actually utilize the detectors to parse the sources from scan

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

    def detectSource(self):
        """This will perform detection the oldest source from SourceData

        Returns:
            bool: If detection process was successful

        """
        sourceData = self.getScheduledSource()
        if sourceData:
            configurationData = self.conf.get_config(sourceData.get('configuration'))
            if configurationData:
                self.ioc.getCollection('SourceData').update_one(
                    {'_id': ObjectId(sourceData.get('_id'))},
                    {
                        'grease_data.detection.detectionStart': datetime.datetime.utcnow()
                    }
                )
                result = self.detection(sourceData.get('data'), configurationData)
                if result:
                    self.ioc.getCollection('SourceData').update_one(
                        {'_id': ObjectId(sourceData.get('_id'))},
                        {
                            'grease_data.detection.detectionEnd': datetime.datetime.utcnow(),
                            'grease_data.detection.detection': result
                        }
                    )
                    # TODO: Schedule to scheduling server
                    return True
                else:
                    self.ioc.getCollection('SourceData').update_one(
                        {'_id': ObjectId(sourceData.get('_id'))},
                        {
                            'grease_data.detection.detectionEnd': datetime.datetime.utcnow(),
                            'grease_data.detection.detection': {}
                        }
                    )
                    self.ioc.getLogger().trace("Detection yielded no detection data", trace=True)
                    return True
            else:
                self.ioc.getLogger().error(
                    "Failed to load Prototype Config [{0}]".format(sourceData.get('configuration')),
                    notify=False
                )
                return False
        else:
            self.ioc.getLogger().trace("No sources awaiting detection currently", trace=True)
            return True

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

    def detection(self, source, configuration):
        """Performs detection on a source with the provided configuration

        Args:
            source (dict): Key->Value pairs from sourcing to detect upon
            configuration (dict): Prototype configuration provided from sourcing

        Returns:
            dict: Detection Results, if empty then detection found no successful logical blocks

        """
        # Ensure types
        if not isinstance(source, dict):
            self.ioc.getLogger().warning("Detection got non-dict source data", notify=False)
            return {}
        if not isinstance(configuration, dict):
            self.ioc.getLogger().warning("Detection got non-dict configuration", notify=False)
            return {}
        # Now loop through logical blocks
        for detector, logicBlock in configuration.items():
            if not isinstance(logicBlock, list):
                self.ioc.getLogger().warning("Logical Block was not list", trace=True, notify=False)
