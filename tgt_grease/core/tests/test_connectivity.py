from unittest import TestCase
from tgt_grease.core import Mongo
import pymongo


class TestConnectivity(TestCase):
    def test_mongo_connection(self):
        mongo = Mongo()
        self.assertTrue(isinstance(mongo.Client(), pymongo.MongoClient))
        mongo.Close()

    def test_mongo_query(self):
        mongo = Mongo()
        client = mongo.Client()
        collection = client.get_database('grease').get_collection('test')
        collection.insert_one({'test': 'var'})
        result = collection.find({'test': 'var'}).count()
        self.assertTrue(result == 1)
        collection.drop()
        del collection
        del client
        mongo.Close()
        del mongo
