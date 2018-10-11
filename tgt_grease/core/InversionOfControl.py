from tgt_grease.core import Logging
from tgt_grease.core.Connectivity import Mongo
from datetime import datetime
from bson.objectid import ObjectId
import platform
import os


class GreaseContainer(object):
    """Inversion of Control Container for objects in GREASE"""

    def __init__(self, *args, **kwargs):
        if args or kwargs:
            self.getLogger().warning(
                "Passing instances of Logger to the IOC is deprecated. Please just use getLogger().", verbose=True
            )
        self.__logger = None
        self.__mongo = None

    def getLogger(self):
        """Get the logging instance

        Returns:
            Logging: The logging instance

        """

        if not isinstance(self.__logger, Logging):
            self.__logger = Logging()

        return self.__logger

    def getNotification(self):
        """Get the notifications instance

        Returns:
            tgt_grease.core.Notifications: The notifications instance

        """
        return self.getLogger().getNotification()

    def getMongo(self):
        """Get the Mongo instance

        Returns:
            Mongo: Mongo Instance Connection

        """

        if not isinstance(self.__mongo, Mongo):
            self.__mongo = Mongo(self.getLogger().getConfig())

        return self.__mongo

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
        return self.getLogger().getConfig()

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
