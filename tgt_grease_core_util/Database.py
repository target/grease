import psycopg2
import psycopg2.extras
import os
import pymongo


class Connection(object):
    @staticmethod
    def create():
        return Connection()

    def __init__(self):
        if os.getenv('GREASE_DSN') is not None:
            self._connection = psycopg2.connect(dsn=os.getenv('GREASE_DSN'))
        else:
            raise EnvironmentError("Failed to find Grease database DSN")
        self._cursor = self._connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def _reload(self):
        self._connection.close()
        self._connection = psycopg2.connect(dsn=os.getenv('GREASE_DSN'))
        self._cursor = self._connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def execute(self, sql, parameters=None):
        # type: (str, tuple) -> None
        self._reload()
        if parameters:
            self._cursor.execute(sql, parameters)
        else:
            self._cursor.execute(sql)
        self._connection.commit()

    def query(self, sql, parameters=None):
        # type: (str, tuple) -> dict
        self._reload()
        if parameters:
            self._cursor.execute(sql, parameters)
        else:
            self._cursor.execute(sql)
        return self._cursor.fetchall()


class MongoConnection(object):
    def __init__(self):
        if not os.getenv('GREASE_MONGO_USER') and not os.getenv('GREASE_MONGO_PASSWORD'):
            self._client = pymongo.MongoClient(
                host=os.getenv('GREASE_MONGO_HOST', 'localhost'),
                port=os.getenv('GREASE_MONGO_PORT', 27017)
            )
        else:
            self._client = pymongo.MongoClient(
                "mongodb://{0}:{1}@{2}:{3}/{4}".format(
                    os.getenv('GREASE_MONGO_USER', ''),
                    os.getenv('GREASE_MONGO_PASSWORD', ''),
                    os.getenv('GREASE_MONGO_HOST', 'localhost'),
                    os.getenv('GREASE_MONGO_PORT', 27017),
                    os.getenv('GREASE_MONGO_DB', 'grease')
                )
            )

    def client(self):
        # type: () -> pymongo.MongoClient
        return self._client
