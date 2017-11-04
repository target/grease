from unittest import TestCase
from tgt_grease.core import GreaseContainer
from tgt_grease.router.Commands.Daemon import DaemonProcess
from bson import ObjectId


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
            'node': ObjectId(ioc.getConfig().NodeIdentity),
            'inProgress': False,
            'completed': False,
            'failures': 0,
            'command': 'help',
            'context': {}
        }).inserted_id
        # Run for a bit
        self.assertTrue(cmd.server())
        self.assertTrue(cmd.drain_jobs(ioc.getCollection('JobQueue')))
        result = ioc.getCollection('JobQueue').find_one({'_id': jobid})
        self.assertTrue(result)
        self.assertTrue(result['completed'])
