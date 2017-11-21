from unittest import TestCase
from tgt_grease.enterprise.Model import Detect, Deduplication
from bson.objectid import ObjectId
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
