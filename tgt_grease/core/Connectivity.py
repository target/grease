import pymongo
from tgt_grease.core import Configuration


class Mongo(object):
    """MongoDB Connection Class

    Attributes:
        _client (pymongo.MongoClient): The actual PyMongo Connection
        _config (Configuration): Configuration Object

    """

    _client = None
    _config = None

    def __init__(self, Config=None):
        if Config and isinstance(Config, Configuration):
            self._config = Config
        else:
            self._config = Configuration()
        self._client = self._generate_client()

    def Client(self):
        """get the connection client

        Returns:
            pymongo.MongoClient: Returns the mongoDB connection client

        """
        return self._client

    def Close(self):
        """Close PyMongo Connection

        Returns:
            None: Void Method to close connection

        """
        self._client.close()

    def _generate_client(self):
        """Creates a PyMongo Client

        Returns:
            pymongo.MongoClient: Mongo Connection

        """
        mongoConf = self._config.get('Connectivity', 'MongoDB')  # type: dict
        if mongoConf.get('username') and mongoConf.get('password'):
            return pymongo.MongoClient(
                "mongodb://{0}:{1}@{2}:{3}/{4}".format(
                    mongoConf.get('username', ''),
                    mongoConf.get('password', ''),
                    mongoConf.get('host', 'localhost'),
                    mongoConf.get('port', 27017),
                    mongoConf.get('db', 'grease')
                ),
                w=1
            )
        else:
            return pymongo.MongoClient(
                host=mongoConf.get('host', 'localhost'),
                port=mongoConf.get('port', 27017),
                w=1
            )
