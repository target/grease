from tgt_grease.core import GreaseContainer
from bson.objectid import ObjectId
from .DeDuplication import Deduplication
import pymongo
import datetime


class Scheduling(object):
    """Central scheduling class for GREASE

    This class routes data to nodes within GREASE

    Attributes:
        ioc (GreaseContainer): IoC access for DeDuplication

    """

    def __init__(self, ioc):
        if isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()

    def scheduleDetection(self, source, data):
        """Schedule a Source Parse to detection

        This method will take a list of single dimension dictionaries and schedule them for detection

        Args:
            source (str): Name of the source
            data (list[dict]): Data to be scheduled for detection

        Returns:
            bool: Scheduling success

        """
        if len(data) is 0 or not isinstance(data, list):
            self.ioc.getLogger().trace(
                "Data provided empty or is not type list type: [{0}] len: [{1}]".format(str(type(data)), len(data)),
                trace=True
            )
            return False
        self.ioc.getLogger().trace("Preparing to schedule [{0}] source objects".format(len(data)), trace=True)
        sourceCollect = self.ioc.getCollection('SourceData')
        jServerCollect = self.ioc.getCollection('JobServer')
        # begin scheduling loop of each block
        for elem in data:
            if not isinstance(elem, dict):
                self.ioc.getLogger().warning(
                    "Element from data not of type dict! Got [{0}] DROPPED".format(str(type(elem))),
                    notify=False
                )
                continue
            server, jobCount = self.determineDetectionServer()
            if server:
                sourceCollect.insert_one({
                    'source': str(source).encode('utf-8'),
                    'data': elem,
                    'createTime': datetime.datetime.utcnow(),
                    'expiry': Deduplication.generate_max_expiry_time(1),
                    'detectionServer': ObjectId(server),
                    'detectionStart': None,
                    'detectionEnd': None,
                    'detectionCompleted': False,
                    'schedulingServer': None,
                    'schedulingStart': None,
                    'schedulingEnd': None,
                    'schedulingCompleted': False
                })
                jServerCollect.update_one({
                    '_id': ObjectId(server)},
                    {'$set': {'jobs': int(jobCount) + 1}}
                )
            else:
                self.ioc.getLogger().warning(
                    "Failed to find detection server for data object from source [{0}]; DROPPED".format(source),
                    notify=False
                )
                self.ioc.getLogger().warning(
                    "Detection scheduling failed. Could not find detection server",
                    notify=False
                )
                return False
        return True

    def determineDetectionServer(self):
        """Determines detection server to use

        Finds the detection server available for a new detection job

        Returns:
            str: MongoDB Object ID of server; if one cannot be found then string will be empty

        """
        result = self.ioc.getCollection('JobServer').find({
            'prototypes': 'detect'
        }).sort('jobs', pymongo.DESCENDING).limit(1)
        if result:
            return str(result[0]['_id']), int(result[0]['jobs'])
        else:
            return ""

    def determineSchedulingServer(self):
        """Determines scheduling server to use

        Finds the scheduling server available for a new scheduling job

        Returns:
            str: MongoDB Object ID of server; if one cannot be found then string will be empty

        """
        result = self.ioc.getCollection('JobServer').find({
            'prototypes': 'schedule'
        }).sort('jobs', pymongo.DESCENDING).limit(1)
        if result:
            return str(result['_id']), int(result['jobs'])
        else:
            return ""

    def determineExecutionServer(self, role):
        """Determines execution server to use

        Finds the execution server available for a new execution job

        Returns:
            str: MongoDB Object ID of server; if one cannot be found then string will be empty

        """
        result = self.ioc.getCollection('JobServer').find({
            'roles': str(role)
        }).sort('jobs', pymongo.DESCENDING).limit(1)
        if result:
            return str(result['_id']), int(result['jobs'])
        else:
            return ""
