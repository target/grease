from unittest import TestCase
from tgt_grease.core import GreaseContainer
from tgt_grease.enterprise.Model import Scheduling, Detect, PrototypeConfig, Deduplication
from bson.objectid import ObjectId
import datetime
import platform
import time
import pymongo


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
                'activationTime': datetime.datetime.utcnow()
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
                'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        time.sleep(1)
        jID2 = jServer.insert_one({
                'jobs': 0,
                'os': platform.system().lower(),
                'roles': ["general"],
                'prototypes': ["detect"],
                'active': True,
                'activationTime': datetime.datetime.utcnow()
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

    def test_scheduleScheduling(self):
        d = Detect()
        p = PrototypeConfig(d.ioc)
        source = {
            'key': 'var',
            'ver': 'key',
            'greg': 'old',
            'created': '2017-11-24'
        }
        configuration = {
            'name': 'demoConfig',
            'job': 'otherThing',
            'exe_env': 'general',
            'source': 'Google',
            'logic': {
                'DateRange': [
                    {
                        'field': 'created',
                        'format': '%Y-%m-%d',
                        'min': '2017-11-23',
                        'max': '2017-11-25'
                    }
                ],
                'Regex': [
                    {
                        'field': 'key',
                        'pattern': '.*',
                        'variable': True,
                        'variable_name': 'field'
                    },
                    {
                        'field': 'ver',
                        'pattern': '.*'
                    }
                ],
                'Exists': [
                    {
                        'field': 'greg',
                        'variable': True,
                        'variable_name': 'greg'
                    }
                ]
            }
        }
        p.load(True, [configuration])
        sourceId = d.ioc.getCollection('SourceData').insert_one({
                    'grease_data': {
                        'sourcing': {
                            'server': ObjectId(d.ioc.getConfig().NodeIdentity)
                        },
                        'detection': {
                            'server': ObjectId(d.ioc.getConfig().NodeIdentity),
                            'detectionStart': None,
                            'detectionEnd': None,
                            'detection': {}
                        },
                        'scheduling': {
                            'schedulingServer': None,
                            'schedulingStart': None,
                            'schedulingEnd': None
                        },
                        'execution': {
                            'server': None,
                            'assignmentTime': None,
                            'executionStart': None,
                            'executionEnd': None,
                            'context': {},
                            'executionSuccess': False,
                            'commandSuccess': False,
                            'failures': 0,
                            'retryTime': datetime.datetime.utcnow()
                        }
                    },
                    'source': str('test').encode('utf-8'),
                    'configuration': configuration.get('name'),
                    'data': source,
                    'createTime': datetime.datetime.utcnow(),
                    'expiry': Deduplication.generate_max_expiry_time(1)
        }).inserted_id
        scheduleServer = d.ioc.getCollection('JobServer').insert_one({
                'jobs': 0,
                'os': platform.system().lower(),
                'roles': ["general"],
                'prototypes': ["schedule"],
                'active': True,
                'activationTime': datetime.datetime.utcnow()
        }).inserted_id
        self.assertTrue(d.detectSource())
        self.assertFalse(d.getScheduledSource())
        self.assertTrue(len(
            d.ioc.getCollection('SourceData').find_one(
                {
                    'grease_data.scheduling.server': ObjectId(scheduleServer),
                    'grease_data.scheduling.start': None,
                    'grease_data.scheduling.end': None
                },
                sort=[('createTime', pymongo.DESCENDING)]
            )
        ))
        d.ioc.getCollection('JobServer').delete_one({'_id': ObjectId(scheduleServer)})
        d.ioc.getCollection('SourceData').delete_one({'_id': ObjectId(sourceId)})
