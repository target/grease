from unittest import TestCase
from tgt_grease.core import GreaseContainer
from tgt_grease.router.Commands.Daemon import DaemonProcess


class TestRegistration(TestCase):
    def test_registration(self):
        ioc = GreaseContainer()
        cmd = DaemonProcess(ioc)
        self.assertTrue(cmd.register())
        collection = ioc.getMongo().Client().get_database('grease').get_collection('JobServer')
        self.assertTrue(collection.find({}).count())
        del collection
        del cmd
        del ioc
