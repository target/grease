from unittest import TestCase
from tgt_grease.core import GreaseContainer, Logging, Configuration, Notifications
from tgt_grease.core.Connectivity import Mongo
from pymongo.collection import Collection


class TestIOC(TestCase):
    def test_logger(self):
        ioc = GreaseContainer()
        self.assertTrue(isinstance(ioc.getLogger(), Logging))

    def test_config(self):
        ioc = GreaseContainer()
        self.assertTrue(isinstance(ioc.getConfig(), Configuration))

    def test_notifications(self):
        ioc = GreaseContainer()
        self.assertTrue(isinstance(ioc.getNotification(), Notifications))

    def test_mongo(self):
        ioc = GreaseContainer()
        self.assertTrue(isinstance(ioc.getMongo(), Mongo))

    def test_get_collection(self):
        ioc = GreaseContainer()
        self.assertTrue(isinstance(ioc.getMongo(), Mongo))
        coll = ioc.getCollection('TestCollection')
        self.assertTrue(isinstance(coll, Collection))
        self.assertEqual(coll.name, "TestCollection")

    def test_registration(self):
        ioc = GreaseContainer()
        self.assertTrue(ioc.ensureRegistration())
