from unittest import TestCase
from tgt_grease.management.Model import BridgeCommand
from bson.objectid import ObjectId


class TestBridge(TestCase):

    def test_registration(self):
        b = BridgeCommand()
        self.assertTrue(b.action_register())

    def test_info(self):
        b = BridgeCommand()
        self.assertTrue(b.action_info(jobs=True, prototypeJobs=True))

    def test_info_with_oid(self):
        b = BridgeCommand()
        self.assertTrue(b.action_info(node=b.ioc.getConfig().NodeIdentity, jobs=True, prototypeJobs=True))

    def test_info_wih_bad_oid(self):
        b = BridgeCommand()
        self.assertFalse(b.action_info(node='32j45koHJO34523o', jobs=True, prototypeJobs=True))

    def test_assignment_operations(self):
        b = BridgeCommand()
        self.assertTrue(b.action_assign(prototype='scan'))
        self.assertTrue(b.action_assign(role='stage'))
        self.assertTrue(b.action_assign(prototype='detect', role='dev'))
        self.assertTrue(b.ioc.getCollection('JobServer').find({
            '_id': ObjectId(b.ioc.getConfig().NodeIdentity),
            'prototypes': 'scan'
        }).count())
        self.assertTrue(b.action_unassign(prototype='scan'))
        self.assertTrue(b.action_unassign(role='stage'))
        self.assertTrue(b.action_unassign(prototype='detect', role='dev'))

    def test_culling_operations(self):
        b = BridgeCommand()
        self.assertTrue(b.action_cull(b.ioc.getConfig().NodeIdentity))
        self.assertTrue(b.ioc.getCollection('JobServer').find({
            '_id': ObjectId(b.ioc.getConfig().NodeIdentity),
            'active': False
        }).count())
        self.assertTrue(b.action_activate(b.ioc.getConfig().NodeIdentity))
        self.assertTrue(b.ioc.getCollection('JobServer').find({
            '_id': ObjectId(b.ioc.getConfig().NodeIdentity),
            'active': True
        }).count())

    def test_node_validation(self):
        b = BridgeCommand()
        valid, server = b.valid_server()
        self.assertTrue(valid)
        valid, server = b.valid_server(b.ioc.getConfig().NodeIdentity)
        self.assertTrue(valid)

    def test_node_validation_failed(self):
        b = BridgeCommand()
        valid, server = b.valid_server('45u32890JKLdsfikojnf')
        self.assertFalse(valid)

