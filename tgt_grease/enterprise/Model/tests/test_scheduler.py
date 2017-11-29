from unittest import TestCase
from tgt_grease.enterprise.Model import Scheduler, PrototypeConfig, Detect, Deduplication
import datetime
from bson.objectid import ObjectId
import pymongo
import platform


class TestScheduler(TestCase):

    def test_schedule_good(self):
        d = Detect()
        p = PrototypeConfig(d.ioc)
        s = Scheduler(d.ioc)
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
        d.ioc.getCollection('JobServer').update_one(
            {'_id': ObjectId(d.ioc.getConfig().NodeIdentity)},
            {
                '$set': {
                    'prototypes': ["scan", "detect", "schedule"]
                }
            }
        )
        self.assertTrue(d.detectSource())
        self.assertFalse(d.getScheduledSource())
        self.assertTrue(s.getDetectedSource())
        self.assertTrue(s.schedule(s.ioc.getCollection('SourceData').find_one({'_id': ObjectId(sourceId)})))
        self.assertTrue(d.ioc.getCollection('JobServer').update_one(
            {'_id': ObjectId(d.ioc.getConfig().NodeIdentity)},
            {
                '$set': {
                    'prototypes': []
                }
            }
        ))
        d.ioc.getCollection('SourceData').delete_one({'_id': ObjectId(sourceId)})

    def test_scheduling(self):
        d = Detect()
        p = PrototypeConfig(d.ioc)
        s = Scheduler(d.ioc)
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
        d.ioc.getCollection('JobServer').update_one(
            {'_id': ObjectId(d.ioc.getConfig().NodeIdentity)},
            {
                '$set': {
                    'prototypes': ["scan", "detect", "schedule"]
                }
            }
        )
        self.assertTrue(d.detectSource())
        self.assertFalse(d.getScheduledSource())
        self.assertTrue(s.getDetectedSource())
        self.assertTrue(s.scheduleExecution())
        self.assertTrue(d.ioc.getCollection('JobServer').update_one(
            {'_id': ObjectId(d.ioc.getConfig().NodeIdentity)},
            {
                '$set': {
                    'prototypes': []
                }
            }
        ))
        d.ioc.getCollection('SourceData').delete_one({'_id': ObjectId(sourceId)})

    def test_scheduling_fail(self):
        d = Detect()
        p = PrototypeConfig(d.ioc)
        s = Scheduler(d.ioc)
        source = {
            'key': 'var',
            'ver': 'key',
            'greg': 'old',
            'created': '2017-11-24'
        }
        configuration = {
            'name': 'demoConfig',
            'job': 'otherThing',
            'exe_env': 'minix',
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
        d.ioc.getCollection('JobServer').update_one(
            {'_id': ObjectId(d.ioc.getConfig().NodeIdentity)},
            {
                '$set': {
                    'prototypes': ["scan", "detect", "schedule"]
                }
            }
        )
        self.assertTrue(d.detectSource())
        self.assertFalse(d.getScheduledSource())
        self.assertTrue(s.getDetectedSource())
        self.assertFalse(s.scheduleExecution())
        self.assertTrue(d.ioc.getCollection('JobServer').update_one(
            {'_id': ObjectId(d.ioc.getConfig().NodeIdentity)},
            {
                '$set': {
                    'prototypes': []
                }
            }
        ))
        d.ioc.getCollection('SourceData').delete_one({'_id': ObjectId(sourceId)})
