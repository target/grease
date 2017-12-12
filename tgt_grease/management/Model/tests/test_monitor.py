from unittest import TestCase
from tgt_grease.management.Model import NodeMonitoring
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
