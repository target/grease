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
            if isinstance(sourceData.get('configuration'), bytes):
                conf = sourceData.get('configuration').decode()
            else:
                conf = sourceData.get('configuration')
            configurationData = self.conf.get_config(conf)
            if configurationData:
                self.ioc.getCollection('SourceData').update_one(
                    {'_id': ObjectId(sourceData.get('_id'))},
                    {
                        '$set': {
                            'grease_data.detection.start': datetime.datetime.utcnow()
                        }
                    }
                )
                result, resultData = self.detection(sourceData.get('data'), configurationData)
                if result:
                    # Put constants in detection results
                    resultData['constants'] = self.conf.get_config(configurationData.get('name')).get('constants', {})
                    # Update detection
                    self.ioc.getCollection('SourceData').update_one(
                        {'_id': ObjectId(sourceData.get('_id'))},
                        {
                            '$set': {
                                'grease_data.detection.end': datetime.datetime.utcnow(),
                                'grease_data.detection.detection': resultData
                            }
                        }
                    )
                    # attempt scheduling
                    return self.scheduler.scheduleScheduling(sourceData.get('_id'))
                else:
                    self.ioc.getCollection('SourceData').update_one(
                        {'_id': ObjectId(sourceData.get('_id'))},
                        {
                            '$set': {
                                'grease_data.detection.end': datetime.datetime.utcnow(),
                                'grease_data.detection.detection': {}
                            }
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
                'grease_data.detection.start': None,
                'grease_data.detection.end': None,
            },
            sort=[('grease_data.createTime', pymongo.DESCENDING)]
        )

    def detection(self, source, configuration):
        """Performs detection on a source with the provided configuration

        Args:
            source (dict): Key->Value pairs from sourcing to detect upon
            configuration (dict): Prototype configuration provided from sourcing

        Returns:
            tuple: Detection Results; first boolean for success, second dict of variables for context

        """
        # Ensure types
        final = {}
        finalBool = False
        if not isinstance(source, dict):
            self.ioc.getLogger().warning("Detection got non-dict source data", notify=False)
            finalBool = False
            return finalBool, final
        if not isinstance(configuration, dict):
            self.ioc.getLogger().warning("Detection got non-dict configuration", notify=False)
            finalBool = False
            return finalBool, final
        # Now loop through logical blocks
        for detector, logicBlock in configuration.get('logic', {}).items():
            if not isinstance(logicBlock, list):
                self.ioc.getLogger().warning("Logical Block was not list", trace=True, notify=False)
            detect = self.impTool.load(detector)
            if isinstance(detect, Detector):
                result, resultData = detect.processObject(source, logicBlock)
                if not result:
                    self.ioc.getLogger().trace("Detection yielded false for [{0}]".format(detector), trace=True)
                    finalBool = False
                    break
                else:
                    self.ioc.getLogger().trace("Detection yielded true for [{0}]".format(detector), trace=True)
                    for key, val in resultData.items():
                        final[key] = val
                    finalBool = True
                    continue
            else:
                self.ioc.getLogger().warning("invalid detector [{0}]".format(detector), notify=False)
                finalBool = False
        return finalBool, final
