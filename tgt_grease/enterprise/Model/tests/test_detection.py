from unittest import TestCase
from tgt_grease.enterprise.Model import Detect, Deduplication, PrototypeConfig
from bson.objectid import ObjectId
import platform
import datetime


class TestDetect(TestCase):

    def test_get_schedule_empty(self):
        d = Detect()
        self.assertFalse(d.getScheduledSource())

    def test_get_schedule_staged(self):
        d = Detect()
        d.ioc.getCollection('SourceData').insert_one({
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
                    'configuration': str('testConfig').encode('utf-8'),
                    'data': {'dev': 'test'},
                    'createTime': datetime.datetime.utcnow(),
                    'expiry': Deduplication.generate_max_expiry_time(1)
        })
        self.assertTrue(d.getScheduledSource())
        self.assertEqual(
            d.getScheduledSource().get('grease_data').get('detection').get('server'),
            ObjectId(d.ioc.getConfig().NodeIdentity)
        )
        d.ioc.getCollection('SourceData').drop()

    def test_detection(self):
        d = Detect()
        source = {
            'key': 'var',
            'ver': 'key',
            'greg': 'old'
        }
        configuration = {
            'name': 'demo config',
            'job': 'otherThing',
            'exe_env': 'general',
            'source': 'Google',
            'logic': {
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
                ]
            }
        }
        result, resultData = d.detection(source, configuration)
        self.assertTrue(result)
        self.assertTrue(resultData.get('field'))

    def test_detection_bad_source(self):
        d = Detect()
        configuration = {
            'name': 'demo config',
            'job': 'otherThing',
            'exe_env': 'general',
            'source': 'Google',
            'logic': {
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
                ]
            }
        }
        result, resultData = d.detection([], configuration)
        self.assertFalse(result)
        self.assertFalse(resultData)

    def test_detection_bad_config(self):
        d = Detect()
        source = {
            'key': 'var',
            'ver': 'key',
            'greg': 'old'
        }
        result, resultData = d.detection(source, [])
        self.assertFalse(result)
        self.assertFalse(resultData)

    def test_detection_failed(self):
        d = Detect()
        source = {
            'key': 'var',
            'ver': 'key',
            'greg': 'old'
        }
        configuration = {
            'name': 'demo config',
            'job': 'otherThing',
            'exe_env': 'general',
            'source': 'Google',
            'logic': {
                'Regex': [
                    {
                        'field': 'ke',
                        'pattern': '.*',
                        'variable': True,
                        'variable_name': 'field'
                    },
                    {
                        'field': 'var',
                        'pattern': '.*'
                    }
                ]
            }
        }
        result, resultData = d.detection(source, configuration)
        self.assertFalse(result)
        self.assertFalse(resultData)

    def test_detection_bad_detector(self):
        d = Detect()
        source = {
            'key': 'var',
            'ver': 'key',
            'greg': 'old'
        }
        configuration = {
            'name': 'demo config',
            'job': 'otherThing',
            'exe_env': 'general',
            'source': 'Google',
            'logic': {
                'regex': [
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
                ]
            }
        }
        result, resultData = d.detection(source, configuration)
        self.assertFalse(result)
        self.assertFalse(resultData)

    def test_detection_bad_logical_block(self):
        d = Detect()
        source = {
            'key': 'var',
            'ver': 'key',
            'greg': 'old'
        }
        configuration = {
            'name': 'demo config',
            'job': 'otherThing',
            'exe_env': 'general',
            'source': 'Google',
            'logic': {
                'Regex': {}
            }
        }
        result, resultData = d.detection(source, configuration)
        self.assertFalse(result)
        self.assertFalse(resultData)

    def test_detection_full(self):
        d = Detect()
        p = PrototypeConfig(d.ioc)
        source = {
            'key': 'var',
            'ver': 'key',
            'greg': 'old'
        }
        configuration = {
            'name': 'demoConfig',
            'job': 'otherThing',
            'exe_env': 'general',
            'source': 'Google',
            'logic': {
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
        d.ioc.getCollection('JobServer').delete_one({'_id': ObjectId(scheduleServer)})
        d.ioc.getCollection('SourceData').delete_one({'_id': ObjectId(sourceId)})

    def test_detection_logic_not_pass(self):
        d = Detect()
        p = PrototypeConfig(d.ioc)
        source = {
            'key': 'var',
            'ver': 'key',
            'greg': 'old'
        }
        configuration = {
            'name': 'demoConfig',
            'job': 'otherThing',
            'exe_env': 'general',
            'source': 'Google',
            'logic': {
                'Regex': [
                    {
                        'field': 'key',
                        'pattern': '.*',
                        'variable': True,
                        'variable_name': 'field'
                    },
                    {
                        'field': 'missingField',
                        'pattern': '.*'
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
        d.ioc.getCollection('JobServer').delete_one({'_id': ObjectId(scheduleServer)})
        d.ioc.getCollection('SourceData').delete_one({'_id': ObjectId(sourceId)})

    def test_detection_full_multi_detector(self):
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
        d.ioc.getCollection('JobServer').delete_one({'_id': ObjectId(scheduleServer)})
        d.ioc.getCollection('SourceData').delete_one({'_id': ObjectId(sourceId)})

    def test_detection_full_multi_detector_fail(self):
        d = Detect()
        p = PrototypeConfig(d.ioc)
        source = {
            'key': 'var',
            'ver': 'key',
            'greg': 'old',
            'created': '2017-11-30'
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
                        'field': 'gary'
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
        item = d.ioc.getCollection('SourceData').find_one({
            '_id': ObjectId(sourceId)
        })
        # Will be false since it failed detection
        self.assertFalse(item['grease_data']['scheduling']['schedulingServer'])
        d.ioc.getCollection('JobServer').delete_one({'_id': ObjectId(scheduleServer)})
        d.ioc.getCollection('SourceData').delete_one({'_id': ObjectId(sourceId)})
