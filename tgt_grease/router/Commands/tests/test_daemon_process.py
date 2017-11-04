from unittest import TestCase
from tgt_grease.core import GreaseContainer
from tgt_grease.core.Types import Command
from tgt_grease.router.Commands.Daemon import DaemonProcess
from bson import ObjectId
from tgt_grease.core import Configuration
import json
import time


class TestProtoType(Command):
    def __init__(self):
        super(TestProtoType, self).__init__()

    def execute(self, context):
        if self.ioc.getCollection('TestProtoType').find({'runs': {'$exists': True}}).count() <= 10:
            for i in range(0, 10):
                self.ioc.getCollection('TestProtoType').insert_one({'runs': i})
        return True


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

    def test_prototype_execution(self):
        ioc = GreaseContainer()
        cmd = DaemonProcess(ioc)
        # add search path
        fil = open(ioc.getConfig().greaseConfigFile, 'r')
        data = json.loads(fil.read())
        fil.close()
        fil = open(ioc.getConfig().greaseConfigFile, 'w')
        data['NodeInformation']['ProtoTypes'] = ['TestProtoType']
        data['Import']['searchPath'].append('tgt_grease.router.Commands.tests')
        fil.write(json.dumps(data, sort_keys=True, indent=4))
        fil.close()
        Configuration.ReloadConfig()
        # Update Node to run it
        ioc.getCollection('JobServer')\
            .update_one(
            {'_id': ObjectId(ioc.getConfig().NodeIdentity)},
            {
                '$set': {
                    'prototypes': ['TestProtoType']
                }
            }
        )
        self.assertTrue(cmd.server())
        self.assertTrue(cmd.drain_jobs(ioc.getCollection('JobQueue')))
        # ensure jobs drain out
        time.sleep(1.5)
        self.assertEqual(
            ioc.getCollection('TestProtoType').find({'runs': {'$exists': True}}).count(),
            10
        )
        # clean up
        fil = open(ioc.getConfig().greaseConfigFile, 'r')
        data = json.loads(fil.read())
        fil.close()
        # remove collection
        ioc.getCollection('TestProtoType').drop()
        # remove prototypes
        data['NodeInformation']['ProtoTypes'] = []
        # pop search path
        trash = data['Import']['searchPath'].pop()
        # close out
        fil = open(ioc.getConfig().greaseConfigFile, 'w')
        fil.write(json.dumps(data, sort_keys=True, indent=4))
        fil.close()
