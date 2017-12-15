from tgt_grease.core import Logging
from tgt_grease.core.Connectivity import Mongo
from datetime import datetime
from bson.objectid import ObjectId
import platform
import os


class GreaseContainer(object):
    """Inversion of Control Container for objects in GREASE"""

    _logger = None
    _mongo = None

    def __init__(self, Logger=None):
        if Logger and isinstance(Logger, Logging):
            self._logger = Logger
        else:
            self._logger = Logging()
        self._mongo = Mongo(self._logger.getConfig())

    def getLogger(self):
        """Get the logging instance

        Returns:
            Logging: The logging instance

        """
        return self._logger

    def getNotification(self):
        """Get the notifications instance

        Returns:
            tgt_grease.core.Notifications: The notifications instance

        """
        return self._logger.getNotification()

    def getMongo(self):
        """Get the Mongo instance

        Returns:
            Mongo: Mongo Instance Connection

        """
        return self._mongo

    def getCollection(self, collectionName):
        """Get a collection object from MongoDB

        Args:
            collectionName (str): Collection to get

        Returns:
            pymongo.collection.Collection: Collection instance

        """
        return self.getMongo()\
            .Client()\
            .get_database(self.getConfig().get('Connectivity', 'MongoDB').get('db', 'grease'))\
            .get_collection(collectionName)

    def getConfig(self):
        """Gets the Configuration Instance

        Returns:
            tgt_grease.core.Configuration.Configuration: the configuration instance

        """
        return self._logger.getConfig()

    def ensureRegistration(self):
        """

        :return:
        """
        collection = self.getCollection("JobServer")
        if os.path.isfile(self.getConfig().greaseDir + 'grease.identity'):
            # check to see if identity file is valid
            fil = open(self.getConfig().greaseDir + 'grease.identity', 'r')
            nodeId = "".join(fil.read())
            fil.close()
            server = collection.find_one({'_id': ObjectId(nodeId)})
            if server:
                # Valid registration
                self.getConfig().NodeIdentity = nodeId
                return True
            else:
                self.getLogger().warning("Invalid node identity found to exist!")
        if self.getConfig().NodeIdentity == "Unknown":
            # Actual registration
            uid = collection.insert_one({
                'jobs': 0,
                'os': platform.system().lower(),
                'roles': ["general"],
                'prototypes': ["monitor"],
                'active': True,
                'activationTime': datetime.utcnow()
            }).inserted_id
            fil = open(self.getConfig().greaseDir + "grease.identity", "w")
            fil.write(str(uid))
            fil.close()
            self.getConfig().NodeIdentity = uid
            del collection
            return True
        else:
            # Check the Identity is actually registered
            if collection.find({'_id': ObjectId(self.getConfig().NodeIdentity)}).count():
                del collection
                return True
            else:
                self.getLogger().error("Invalid Node Identity::Node Identity Not Found", additional={
                    'NodeID': self.getConfig().NodeIdentity
                })
                del collection
                return False
