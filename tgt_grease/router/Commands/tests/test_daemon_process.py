from unittest import TestCase
from tgt_grease.core import GreaseContainer
from tgt_grease.router.Commands.Daemon import DaemonProcess
import time


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

    def test_job_execution(self):
        ioc = GreaseContainer()
        cmd = DaemonProcess(ioc)
        jobid = ioc.getCollection('JobQueue').insert_one({
            'node': ioc.getConfig().NodeIdentity,
            'inProgress': False,
            'completed': False,
            'failures': 0,
            'command': 'help',
            'context': {}
        }).inserted_id
        # Run for a bit
        for r in range(0, 10):
            self.assertTrue(cmd.server())
            print ioc.getConfig().NodeIdentity
            time.sleep(.5)
        result = ioc.getCollection('JobQueue').find_one({'_id': jobid})
        self.assertTrue(result)
        self.assertTrue(result['completed'])
