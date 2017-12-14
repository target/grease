from unittest import TestCase
from tgt_grease.management.Model import NodeMonitoring
from tgt_grease.enterprise.Model import Deduplication
from tgt_grease.enterprise.Model import PrototypeConfig
from bson.objectid import ObjectId
import datetime
import platform


class TestNodeMonitoring(TestCase):

    def test_get_servers(self):
        n = NodeMonitoring()
        server = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 10,
            'os': platform.system().lower(),
            'roles': [],
            'prototypes': [],
            'active': True,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        result = n.getServers()
        self.assertGreaterEqual(len(result), 1)
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server}).deleted_count,
            1
        )

    def test_get_servers_inactive_server(self):
        n = NodeMonitoring()
        server = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 10,
            'os': platform.system().lower(),
            'roles': [],
            'prototypes': [],
            'active': False,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        result = n.getServers()
        self.assertLessEqual(len(result), 1)
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server}).deleted_count,
            1
        )
        n.ioc.getCollection('ServerHealth').drop()

    def test_monitor(self):
        n = NodeMonitoring()
        p = PrototypeConfig(n.ioc)
        server1 = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 9,
            'os': platform.system().lower(),
            'roles': [],
            'prototypes': [],
            'active': True,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        server2 = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 9,
            'os': platform.system().lower(),
            'roles': ['test'],
            'prototypes': ['detect', 'schedule'],
            'active': True,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        config = n.ioc.getCollection('Configuration').insert_one(
            {
                'active': True,
                'type': 'prototype_config',
                "name": "test",
                "job": "help",
                "exe_env": "test",
                "source": "test",
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
        ).inserted_id
        p.load(reloadConf=True)
        source = n.ioc.getCollection('SourceData').insert_one({
            'grease_data': {
                'sourcing': {
                    'server': server1
                },
                'detection': {
                    'server': server1,
                    'start': datetime.datetime.utcnow(),
                    'end': datetime.datetime.utcnow(),
                    'detection': {}
                },
                'scheduling': {
                    'server': server1,
                    'start': datetime.datetime.utcnow(),
                    'end': datetime.datetime.utcnow(),
                },
                'execution': {
                    'server': server1,
                    'assignmentTime': datetime.datetime.utcnow(),
                    'completeTime': None,
                    'returnData': {},
                    'executionSuccess': False,
                    'commandSuccess': False,
                    'failures': 0
                }
            },
            'source': 'test',
            'configuration': 'test',
            'createTime': datetime.datetime.utcnow(),
            'expiry': Deduplication.generate_max_expiry_time(1)
        }).inserted_id
        self.assertTrue(n.monitor())
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server1}).deleted_count,
            1
        )
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server2}).deleted_count,
            1
        )
        n.ioc.getCollection('SourceData').delete_one({'_id': source})
        n.ioc.getCollection('Configuration').delete_one({'_id': config})
        n.ioc.getCollection('ServerHealth').drop()

    def test_scanComplete(self):
        n = NodeMonitoring()
        originalServer = n.ioc.getCollection('JobServer').find_one({'_id': ObjectId(n.ioc.getConfig().NodeIdentity)})
        self.assertTrue(originalServer)
        originalServer = dict(originalServer)
        originalSourcing = n.ioc.getCollection('SourceData').find(
            {'grease_data.execution.server': ObjectId(originalServer.get('_id'))}
        ).count()
        n.scanComplete()
        newSourcing = n.ioc.getCollection('SourceData').find(
            {'grease_data.execution.server': ObjectId(originalServer.get('_id'))}
        ).count()
        newServer = n.ioc.getCollection('JobServer').find_one({'_id': ObjectId(n.ioc.getConfig().NodeIdentity)})
        self.assertTrue(newServer)
        newServer = dict(newServer)
        self.assertGreaterEqual(newSourcing, originalSourcing)
        self.assertGreaterEqual(newServer.get('jobs'), originalServer.get('jobs'))
        n.ioc.getCollection('SourceData').drop()
        n.ioc.getCollection('JobServer').update_one(
            {'_id': ObjectId(originalServer.get('_id'))},
            {
                '$set': {
                    'jobs': originalServer.get('jobs', 0)
                }
            }
        )

    def test_serverAliveNewServerGood(self):
        n = NodeMonitoring()
        server = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 10,
            'os': platform.system().lower(),
            'roles': [],
            'prototypes': [],
            'active': False,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        self.assertTrue(n.serverAlive(str(server)))
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server}).deleted_count,
            1
        )
        n.ioc.getCollection('ServerHealth').drop()

    def test_serverAliveCurrentServerGood(self):
        n = NodeMonitoring()
        server = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 10,
            'os': platform.system().lower(),
            'roles': [],
            'prototypes': [],
            'active': False,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        n.ioc.getCollection('ServerHealth').insert_one(
            {
                'server': server,
                'jobs': 9,
                'checkTime': datetime.datetime.utcnow()
            }
        )
        self.assertTrue(n.serverAlive(str(server)))
        self.assertEqual(n.ioc.getCollection('ServerHealth').find({
            'server': server,
            'jobs': 10
        }).count(), 1)
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server}).deleted_count,
            1
        )
        n.ioc.getCollection('ServerHealth').drop()

    def test_serverAliveCurrentServerDegraded(self):
        n = NodeMonitoring()
        server = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 9,
            'os': platform.system().lower(),
            'roles': [],
            'prototypes': [],
            'active': False,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        n.ioc.getCollection('ServerHealth').insert_one(
            {
                'server': server,
                'jobs': 9,
                'checkTime': datetime.datetime.utcnow() - datetime.timedelta(minutes=9)
            }
        )
        self.assertTrue(n.serverAlive(str(server)))
        self.assertEqual(n.ioc.getCollection('ServerHealth').find({
            'server': server,
            'jobs': 9
        }).count(), 1)
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server}).deleted_count,
            1
        )
        n.ioc.getCollection('ServerHealth').drop()

    def test_serverAliveCurrentServerDead(self):
        n = NodeMonitoring()
        server = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 9,
            'os': platform.system().lower(),
            'roles': [],
            'prototypes': [],
            'active': False,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        n.ioc.getCollection('ServerHealth').insert_one(
            {
                'server': server,
                'jobs': 9,
                'checkTime': datetime.datetime.utcnow() - datetime.timedelta(minutes=10, seconds=1)
            }
        )
        self.assertFalse(n.serverAlive(str(server)))
        self.assertEqual(n.ioc.getCollection('ServerHealth').find({
            'server': server,
            'jobs': 9
        }).count(), 1)
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server}).deleted_count,
            1
        )
        n.ioc.getCollection('ServerHealth').drop()

    def test_serverDeactivateGood(self):
        n = NodeMonitoring()
        server = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 9,
            'os': platform.system().lower(),
            'roles': [],
            'prototypes': [],
            'active': True,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        self.assertTrue(n.deactivateServer(str(server)))
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server}).deleted_count,
            1
        )
        n.ioc.getCollection('ServerHealth').drop()

    def test_serverDeactivateFailed(self):
        n = NodeMonitoring()
        server = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 9,
            'os': platform.system().lower(),
            'roles': [],
            'prototypes': [],
            'active': False,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server}).deleted_count,
            1
        )
        self.assertFalse(n.deactivateServer(str(server)))
        n.ioc.getCollection('ServerHealth').drop()

    def test_rescheduleDetectJobsGood(self):
        n = NodeMonitoring()
        server1 = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 9,
            'os': platform.system().lower(),
            'roles': [],
            'prototypes': [],
            'active': True,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        server2 = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 9,
            'os': platform.system().lower(),
            'roles': ['test'],
            'prototypes': ['detect', 'schedule'],
            'active': True,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        source = n.ioc.getCollection('SourceData').insert_one({
            'grease_data': {
                'sourcing': {
                    'server': server1
                },
                'detection': {
                    'server': server1,
                    'start': None,
                    'end': None,
                    'detection': {}
                },
                'scheduling': {
                    'server': None,
                    'start': None,
                    'end': None
                },
                'execution': {
                    'server': None,
                    'assignmentTime': None,
                    'completeTime': None,
                    'returnData': {},
                    'executionSuccess': False,
                    'commandSuccess': False,
                    'failures': 0
                }
            },
            'source': 'test',
            'configuration': 'test',
            'data': {'test': 'ver'},
            'createTime': datetime.datetime.utcnow(),
            'expiry': Deduplication.generate_max_expiry_time(1)
        }).acknowledged
        self.assertTrue(n.deactivateServer(str(server1)))
        self.assertTrue(n.rescheduleDetectJobs(str(server1)))
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server1}).deleted_count,
            1
        )
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server2}).deleted_count,
            1
        )
        n.ioc.getCollection('SourceData').delete_one({'_id': source})
        n.ioc.getCollection('ServerHealth').drop()

    def test_rescheduleDetectJobsFailed(self):
        n = NodeMonitoring()
        server1 = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 9,
            'os': platform.system().lower(),
            'roles': [],
            'prototypes': [],
            'active': True,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        n.ioc.getCollection('JobServer').update_many(
            {'active': True},
            {
                '$set': {
                    'prototypes': []
                }
            }
        )
        source = n.ioc.getCollection('SourceData').insert_one({
            'grease_data': {
                'sourcing': {
                    'server': server1
                },
                'detection': {
                    'server': server1,
                    'start': None,
                    'end': None,
                    'detection': {}
                },
                'scheduling': {
                    'server': None,
                    'start': None,
                    'end': None
                },
                'execution': {
                    'server': None,
                    'assignmentTime': None,
                    'completeTime': None,
                    'returnData': {},
                    'executionSuccess': False,
                    'commandSuccess': False,
                    'failures': 0
                }
            },
            'source': 'test',
            'configuration': 'test',
            'data': {'test': 'ver'},
            'createTime': datetime.datetime.utcnow(),
            'expiry': Deduplication.generate_max_expiry_time(1)
        }).acknowledged
        self.assertTrue(n.deactivateServer(str(server1)))
        self.assertFalse(n.rescheduleDetectJobs(str(server1)))
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server1}).deleted_count,
            1
        )
        n.ioc.getCollection('SourceData').delete_one({'_id': source})
        n.ioc.getCollection('ServerHealth').drop()

    def test_rescheduleScheduleJobsGood(self):
        n = NodeMonitoring()
        server1 = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 9,
            'os': platform.system().lower(),
            'roles': [],
            'prototypes': [],
            'active': True,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        server2 = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 9,
            'os': platform.system().lower(),
            'roles': ['test'],
            'prototypes': ['detect', 'schedule'],
            'active': True,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        config = n.ioc.getCollection('Configuration').insert_one(
            {
                'active': True,
                'type': 'prototype_config',
                "name": "test",
                "job": "help",
                "exe_env": "test",
                "source": "test",
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
        ).inserted_id
        source = n.ioc.getCollection('SourceData').insert_one({
            'grease_data': {
                'sourcing': {
                    'server': server1
                },
                'detection': {
                    'server': server1,
                    'start': None,
                    'end': None,
                    'detection': {}
                },
                'scheduling': {
                    'server': None,
                    'start': None,
                    'end': None
                },
                'execution': {
                    'server': None,
                    'assignmentTime': None,
                    'completeTime': None,
                    'returnData': {},
                    'executionSuccess': False,
                    'commandSuccess': False,
                    'failures': 0
                }
            },
            'source': 'test',
            'configuration': 'test',
            'data': {'test': 'ver'},
            'createTime': datetime.datetime.utcnow(),
            'expiry': Deduplication.generate_max_expiry_time(1)
        }).acknowledged
        self.assertTrue(n.deactivateServer(str(server1)))
        self.assertTrue(n.rescheduleScheduleJobs(str(server1)))
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server1}).deleted_count,
            1
        )
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server2}).deleted_count,
            1
        )
        n.ioc.getCollection('SourceData').delete_one({'_id': source})
        n.ioc.getCollection('Configuration').delete_one({'_id': config})
        n.ioc.getCollection('ServerHealth').drop()

    def test_rescheduleScheduleJobsFailed(self):
        n = NodeMonitoring()
        server1 = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 9,
            'os': platform.system().lower(),
            'roles': [],
            'prototypes': [],
            'active': True,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        server2 = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 9,
            'os': platform.system().lower(),
            'roles': ['test'],
            'prototypes': [],
            'active': True,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        config = n.ioc.getCollection('Configuration').insert_one(
            {
                'active': True,
                'type': 'prototype_config',
                "name": "test",
                "job": "help",
                "exe_env": "test",
                "source": "test",
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
        ).inserted_id
        n.ioc.getCollection('JobServer').update_many(
            {'active': True},
            {
                '$set': {
                    'prototypes': []
                }
            }
        )
        source = n.ioc.getCollection('SourceData').insert_one({
            'grease_data': {
                'sourcing': {
                    'server': server1
                },
                'detection': {
                    'server': server1,
                    'start': None,
                    'end': None,
                    'detection': {}
                },
                'scheduling': {
                    'server': server1,
                    'start': None,
                    'end': None
                },
                'execution': {
                    'server': None,
                    'assignmentTime': None,
                    'completeTime': None,
                    'returnData': {},
                    'executionSuccess': False,
                    'commandSuccess': False,
                    'failures': 0
                }
            },
            'source': 'test',
            'configuration': 'test',
            'data': {'test': 'ver'},
            'createTime': datetime.datetime.utcnow(),
            'expiry': Deduplication.generate_max_expiry_time(1)
        }).acknowledged
        self.assertTrue(n.deactivateServer(str(server1)))
        self.assertFalse(n.rescheduleScheduleJobs(str(server1)))
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server1}).deleted_count,
            1
        )
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server2}).deleted_count,
            1
        )
        n.ioc.getCollection('SourceData').delete_one({'_id': source})
        n.ioc.getCollection('Configuration').delete_one({'_id': config})
        n.ioc.getCollection('ServerHealth').drop()

    def test_rescheduleJobsGood(self):
        n = NodeMonitoring()
        p = PrototypeConfig(n.ioc)
        server1 = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 9,
            'os': platform.system().lower(),
            'roles': [],
            'prototypes': [],
            'active': True,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        server2 = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 9,
            'os': platform.system().lower(),
            'roles': ['test'],
            'prototypes': ['detect', 'schedule'],
            'active': True,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        config = n.ioc.getCollection('Configuration').insert_one(
            {
                'active': True,
                'type': 'prototype_config',
                "name": "test",
                "job": "help",
                "exe_env": "test",
                "source": "test",
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
        ).inserted_id
        p.load(reloadConf=True)
        source = n.ioc.getCollection('SourceData').insert_one({
            'grease_data': {
                'sourcing': {
                    'server': server1
                },
                'detection': {
                    'server': server1,
                    'start': datetime.datetime.utcnow(),
                    'end': datetime.datetime.utcnow(),
                    'detection': {}
                },
                'scheduling': {
                    'server': server1,
                    'start': datetime.datetime.utcnow(),
                    'end': datetime.datetime.utcnow(),
                },
                'execution': {
                    'server': server1,
                    'assignmentTime': datetime.datetime.utcnow(),
                    'completeTime': None,
                    'returnData': {},
                    'executionSuccess': False,
                    'commandSuccess': False,
                    'failures': 0
                }
            },
            'source': 'test',
            'configuration': 'test',
            'createTime': datetime.datetime.utcnow(),
            'expiry': Deduplication.generate_max_expiry_time(1)
        }).inserted_id
        self.assertTrue(n.deactivateServer(str(server1)))
        self.assertTrue(n.rescheduleJobs(str(server1)))
        self.assertTrue(n.ioc.getCollection('SourceData').find({
            '_id': source,
            'grease_data.execution.server': server2
        }).count())
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server1}).deleted_count,
            1
        )
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server2}).deleted_count,
            1
        )
        n.ioc.getCollection('SourceData').delete_one({'_id': source})
        n.ioc.getCollection('Configuration').drop()
        n.ioc.getCollection('ServerHealth').drop()
        p.load(reloadConf=True)

    def test_rescheduleJobsFailed(self):
        n = NodeMonitoring()
        p = PrototypeConfig(n.ioc)
        server1 = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 9,
            'os': platform.system().lower(),
            'roles': [],
            'prototypes': [],
            'active': True,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        server2 = n.ioc.getCollection('JobServer').insert_one({
            'jobs': 9,
            'os': platform.system().lower(),
            'roles': ['test1'],
            'prototypes': ['detect', 'schedule'],
            'active': True,
            'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        config = n.ioc.getCollection('Configuration').insert_one(
            {
                'active': True,
                'type': 'prototype_config',
                "name": "test",
                "job": "help",
                "exe_env": "test",
                "source": "test",
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
        ).inserted_id
        p.load(reloadConf=True)
        source = n.ioc.getCollection('SourceData').insert_one({
            'grease_data': {
                'sourcing': {
                    'server': server1
                },
                'detection': {
                    'server': server1,
                    'start': datetime.datetime.utcnow(),
                    'end': datetime.datetime.utcnow(),
                    'detection': {}
                },
                'scheduling': {
                    'server': server1,
                    'start': datetime.datetime.utcnow(),
                    'end': datetime.datetime.utcnow(),
                },
                'execution': {
                    'server': server1,
                    'assignmentTime': datetime.datetime.utcnow(),
                    'completeTime': None,
                    'returnData': {},
                    'executionSuccess': False,
                    'commandSuccess': False,
                    'failures': 0
                }
            },
            'source': 'test',
            'configuration': 'test',
            'createTime': datetime.datetime.utcnow(),
            'expiry': Deduplication.generate_max_expiry_time(1)
        }).inserted_id
        self.assertTrue(n.deactivateServer(str(server1)))
        self.assertFalse(n.rescheduleJobs(str(server1)))
        self.assertFalse(n.ioc.getCollection('SourceData').find({
            '_id': source,
            'grease_data.execution.server': server2
        }).count())
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server1}).deleted_count,
            1
        )
        self.assertEqual(
            n.ioc.getCollection('JobServer').delete_one({'_id': server2}).deleted_count,
            1
        )
        n.ioc.getCollection('SourceData').delete_one({'_id': source})
        n.ioc.getCollection('Configuration').drop()
        n.ioc.getCollection('ServerHealth').drop()
        p.load(reloadConf=True)
