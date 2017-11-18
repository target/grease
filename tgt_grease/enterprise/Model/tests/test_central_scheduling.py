from unittest import TestCase
from tgt_grease.core import GreaseContainer
from tgt_grease.enterprise.Model import Scheduling
from bson.objectid import ObjectId
from datetime import datetime
import platform
import time


class TestScheduling(TestCase):

    def test_empty_source_schedule(self):
        ioc = GreaseContainer()
        sch = Scheduling(ioc)
        jServer = ioc.getCollection('JobServer')
        jID = jServer.insert_one({
                'jobs': 0,
                'os': platform.system().lower(),
                'roles': ["general"],
                'prototypes': ["detect"],
                'active': True,
                'activationTime': datetime.utcnow()
        }).inserted_id
        time.sleep(1.5)
        self.assertFalse(sch.scheduleDetection('test', 'test_conf', []))
        jServer.delete_one({'_id': ObjectId(jID)})
        ioc.getCollection('SourceData').drop()

    def test_detectionScheduling(self):
        ioc = GreaseContainer()
        ioc.ensureRegistration()
        sch = Scheduling(ioc)
        jServer = ioc.getCollection('JobServer')
        jID1 = jServer.insert_one({
                'jobs': 0,
                'os': platform.system().lower(),
                'roles': ["general"],
                'prototypes': ["detect"],
                'active': True,
                'activationTime': datetime.utcnow()
        }).inserted_id
        time.sleep(1)
        jID2 = jServer.insert_one({
                'jobs': 0,
                'os': platform.system().lower(),
                'roles': ["general"],
                'prototypes': ["detect"],
                'active': True,
                'activationTime': datetime.utcnow()
        }).inserted_id
        time.sleep(1)
        self.assertTrue(sch.scheduleDetection('test', 'test_conf', [
            {
                'test0': 'var0',
                'test1': 'var1',
                'test2': 'var2',
                'test3': 'var3',
                'test4': 'var4',
                'test5': 'var5',
                'test6': 'var6',
                'test7': 'var7',
                'test8': 'var8',
                'test9': 'var9',
                'test10': 'var10',
            },
            {
                'test0': 'var0',
                'test1': 'var1',
                'test2': 'var2',
                'test3': 'var3',
                'test4': 'var4',
                'test5': 'var5',
                'test6': 'var6',
                'test7': 'var7',
                'test8': 'var8',
                'test9': 'var9',
                'test10': 'var10',
            },
            {
                'test0': 'var0',
                'test1': 'var1',
                'test2': 'var2',
                'test3': 'var3',
                'test4': 'var4',
                'test5': 'var5',
                'test6': 'var6',
                'test7': 'var7',
                'test8': 'var8',
                'test9': 'var9',
                'test10': 'var10',
            },
            {
                'test0': 'var0',
                'test1': 'var1',
                'test2': 'var2',
                'test3': 'var3',
                'test4': 'var4',
                'test5': 'var5',
                'test6': 'var6',
                'test7': 'var7',
                'test8': 'var8',
                'test9': 'var9',
                'test10': 'var10',
            },
            {
                'test0': 'var0',
                'test1': 'var1',
                'test2': 'var2',
                'test3': 'var3',
                'test4': 'var4',
                'test5': 'var5',
                'test6': 'var6',
                'test7': 'var7',
                'test8': 'var8',
                'test9': 'var9',
                'test10': 'var10',
            },
            {
                'test0': 'var0',
                'test1': 'var1',
                'test2': 'var2',
                'test3': 'var3',
                'test4': 'var4',
                'test5': 'var5',
                'test6': 'var6',
                'test7': 'var7',
                'test8': 'var8',
                'test9': 'var9',
                'test10': 'var10',
            },
        ]))
        time.sleep(1)
        self.assertEqual(ioc.getCollection('SourceData').find({
            'grease_data.detection.server': ObjectId(jID1)
        }).count(), 3)
        self.assertEqual(ioc.getCollection('SourceData').find({
            'grease_data.detection.server': ObjectId(jID2)
        }).count(), 3)
        self.assertEqual(ioc.getCollection('JobServer').find_one({
            '_id': ObjectId(jID1)
        })['jobs'], 3)
        self.assertEqual(ioc.getCollection('JobServer').find_one({
            '_id': ObjectId(jID2)
        })['jobs'], 3)
        jServer.delete_one({'_id': ObjectId(jID1)})
        jServer.delete_one({'_id': ObjectId(jID2)})
        ioc.getCollection('SourceData').drop()
