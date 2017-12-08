from unittest import TestCase
from tgt_grease.core import GreaseContainer
from tgt_grease.core.Types import Command
from tgt_grease.router.Commands.Daemon import DaemonProcess
from tgt_grease.enterprise.Model import Deduplication, PrototypeConfig
from bson import ObjectId
from tgt_grease.core import Configuration
import json
import datetime
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
        proto = PrototypeConfig(ioc)
        ioc.getCollection('Configuration').insert_one(
            {
                'active': True,
                'type': 'prototype_config',
                "name": "exe_test",
                "job": "help",
                "exe_env": "general",
                "source": "url_source",
                "logic": {
                    "Regex": [
                        {
                            "field": "url",
                            "pattern": ".*",
                            'variable': True,
                            'variable_name': 'url'
                        }
                    ],
                    'Range': [
                        {
                            'field': 'status_code',
                            'min': 199,
                            'max': 201
                        }
                    ]
                },
                'constants': {
                    'test': 'ver'
                }
            }
        )
        proto.load(reloadConf=True)
        jobid = ioc.getCollection('SourceData').insert_one({
                    'grease_data': {
                        'sourcing': {
                            'server': ObjectId(ioc.getConfig().NodeIdentity)
                        },
                        'detection': {
                            'server': ObjectId(ioc.getConfig().NodeIdentity),
                            'start': datetime.datetime.utcnow(),
                            'end': datetime.datetime.utcnow(),
                            'detection': {}
                        },
                        'scheduling': {
                            'server': ObjectId(ioc.getConfig().NodeIdentity),
                            'start': datetime.datetime.utcnow(),
                            'end': datetime.datetime.utcnow(),
                        },
                        'execution': {
                            'server': ObjectId(ioc.getConfig().NodeIdentity),
                            'assignmentTime': datetime.datetime.utcnow(),
                            'completeTime': None,
                            'returnData': {},
                            'executionSuccess': False,
                            'commandSuccess': False,
                            'failures': 0
                        }
                    },
                    'source': 'dev',
                    'configuration': 'exe_test',
                    'data': {},
                    'createTime': datetime.datetime.utcnow(),
                    'expiry': Deduplication.generate_max_expiry_time(1)
                }).inserted_id
        # Run for a bit
        self.assertTrue(cmd.server())
        self.assertTrue(cmd.drain_jobs(ioc.getCollection('SourceData')))
        result = ioc.getCollection('SourceData').find_one({'_id': ObjectId(jobid)})
        self.assertTrue(result)
        self.assertTrue(result.get('grease_data').get('execution').get('executionSuccess'))
        self.assertTrue(result.get('grease_data').get('execution').get('commandSuccess'))
        ioc.getCollection('SourceData').drop()
        ioc.getCollection('Configuration').drop()

    def test_prototype_execution(self):
        ioc = GreaseContainer()
        cmd = DaemonProcess(ioc)
        # add search path
        fil = open(ioc.getConfig().greaseConfigFile, 'r')
        data = json.loads(fil.read())
        fil.close()
        fil = open(ioc.getConfig().greaseConfigFile, 'w')
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
        # Sleeps are because mongo in Travis is slow sometimes to persist data
        time.sleep(1.5)
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
        # pop search path
        trash = data['Import']['searchPath'].pop()
        # close out
        fil = open(ioc.getConfig().greaseConfigFile, 'w')
        fil.write(json.dumps(data, sort_keys=True, indent=4))
        fil.close()
        ioc.getCollection('JobServer') \
            .update_one(
            {'_id': ObjectId(ioc.getConfig().NodeIdentity)},
            {
                '$set': {
                    'prototypes': []
                }
            }
        )
