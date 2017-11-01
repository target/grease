from unittest import TestCase
from tgt_grease.core import GreaseContainer, Logging, Configuration, Notifications
from tgt_grease.core.Connectivity import Mongo


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
