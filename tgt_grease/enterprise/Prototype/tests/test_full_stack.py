from unittest import TestCase
from tgt_grease.core import GreaseContainer
from tgt_grease.enterprise.Model import PrototypeConfig
from tgt_grease.enterprise.Prototype import scan, detect, schedule
from tgt_grease.router.Commands.Daemon import DaemonProcess
from bson.objectid import ObjectId
import json
import os
import time


class TestFullStack(TestCase):

    def test_mock(self):
        #############################################
        #            SETUP UP TIME
        #############################################
        ioc = GreaseContainer()
        pConf = PrototypeConfig(ioc)
        ioc.ensureRegistration()
        ioc.getCollection('JobServer').update_one(
            {'_id': ObjectId(ioc.getConfig().NodeIdentity)},
            {
                '$set': {
                    'prototypes': ['scan', 'detect', 'schedule']
                }
            }
        )
        ioc.getCollection('Configuration').insert_one(
            {
                'active': True,
                'type': 'prototype_config',
                "name": "full_stack_test",
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
        pConf.load(reloadConf=True)
        TestFile = ioc.getConfig().get('Sourcing', 'dir') + 'full_stack.mock.url.json'
        with open(TestFile, 'w') as fil:
            fil.write(json.dumps({
                'url': 'https://google.com',
                'status_code': 200,
                'headers': str({'test': 'var'}),
                'body': 'test data'
            }, indent=4))
        #############################################
        #            EXECUTE SCANNING
        #############################################
        Scanner = scan()
        Scanner.ioc.getLogger().getConfig().set('verbose', True, 'Logging')
        Scanner.ioc.getLogger().getConfig().set('trace', True, 'Logging')
        Scanner.ioc.getLogger().getConfig().set('mock', True, 'Sourcing')
        Scanner.ioc.getLogger().getConfig().set('config', 'full_stack_test', 'Sourcing')
        self.assertTrue(Scanner.execute({'loop': 1}))
        #############################################
        #            ASSERT SCANNING
        #############################################
        self.assertTrue(ioc.getCollection('SourceData').find_one({
            'grease_data.sourcing.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.detection.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.detection.start': None,
            'grease_data.detection.end': None
        }))
        #############################################
        #            EXECUTE DETECTION
        #############################################
        Detect = detect()
        Detect.ioc.getLogger().getConfig().set('verbose', True, 'Logging')
        Detect.ioc.getLogger().getConfig().set('trace', True, 'Logging')
        Detect.ioc.getLogger().getConfig().set('mock', True, 'Sourcing')
        Detect.ioc.getLogger().getConfig().set('config', 'full_stack_test', 'Sourcing')
        self.assertTrue(Detect.execute({'loop': 1}))
        #############################################
        #            ASSERT DETECTION
        #############################################
        self.assertTrue(ioc.getCollection('SourceData').find_one({
            'grease_data.sourcing.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.detection.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.detection.detection.url': ['https://google.com', ''],
            'grease_data.detection.detection.constants.test': 'ver',
            'grease_data.scheduling.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.scheduling.start': None,
            'grease_data.scheduling.end': None
        }))
        #############################################
        #            EXECUTE SCHEDULING
        #############################################
        Scheduling = schedule()
        Scheduling.ioc.getLogger().getConfig().set('verbose', True, 'Logging')
        Scheduling.ioc.getLogger().getConfig().set('trace', True, 'Logging')
        Scheduling.ioc.getLogger().getConfig().set('mock', True, 'Sourcing')
        Scheduling.ioc.getLogger().getConfig().set('config', 'full_stack_test', 'Sourcing')
        self.assertTrue(Scheduling.execute({'loop': 1}))
        #############################################
        #            ASSERT SCHEDULING
        #############################################
        self.assertTrue(ioc.getCollection('SourceData').find_one({
            'grease_data.sourcing.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.detection.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.detection.detection.url': ['https://google.com', ''],
            'grease_data.detection.detection.constants.test': 'ver',
            'grease_data.scheduling.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.execution.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.execution.start': None,
            'grease_data.execution.end': None
        }))
        #############################################
        #            EXECUTE JOBS
        #############################################
        ioc.getCollection('JobServer').update_one(
            {'_id': ObjectId(ioc.getConfig().NodeIdentity)},
            {
                '$set': {
                    'prototypes': []
                }
            }
        )
        Daemon = DaemonProcess(ioc)
        Daemon.ioc.getLogger().getConfig().set('verbose', True, 'Logging')
        Daemon.ioc.getLogger().getConfig().set('trace', True, 'Logging')
        Daemon.ioc.getLogger().getConfig().set('mock', True, 'Sourcing')
        Daemon.ioc.getLogger().getConfig().set('config', 'full_stack_test', 'Sourcing')
        self.assertTrue(Daemon.server())
        self.assertTrue(Daemon.drain_jobs(ioc.getCollection('SourceData')))
        #############################################
        #            ASSERT JOB EXECUTION
        #############################################
        # sleep a few for seconds to let help complete
        time.sleep(5)
        self.assertTrue(ioc.getCollection('SourceData').find_one({
            'grease_data.sourcing.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.detection.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.detection.detection.url': ['https://google.com', ''],
            'grease_data.detection.detection.constants.test': 'ver',
            'grease_data.scheduling.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.execution.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.execution.commandSuccess': True,
            'grease_data.execution.executionSuccess': True
        }))
        #############################################
        #            CLEAN UP TIME
        #############################################
        ioc.getCollection('JobServer').update_one(
            {'_id': ObjectId(ioc.getConfig().NodeIdentity)},
            {
                '$set': {
                    'prototypes': []
                }
            }
        )
        ioc.getCollection('Configuration').drop()
        ioc.getCollection('SourceData').drop()
        pConf.load(reloadConf=True)
        os.remove(TestFile)

    def test_real(self):
        #############################################
        #            SETUP UP TIME
        #############################################
        ioc = GreaseContainer()
        pConf = PrototypeConfig(ioc)
        ioc.ensureRegistration()
        ioc.getCollection('JobServer').update_one(
            {'_id': ObjectId(ioc.getConfig().NodeIdentity)},
            {
                '$set': {
                    'prototypes': ['scan', 'detect', 'schedule']
                }
            }
        )
        ioc.getCollection('Configuration').insert_one(
            {
                'active': True,
                'type': 'prototype_config',
                "name": "full_stack_test",
                "job": "help",
                "exe_env": "general",
                "source": "url_source",
                "url": ['http://google.com'],
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
        pConf.load(reloadConf=True)
        #############################################
        #            EXECUTE SCANNING
        #############################################
        Scanner = scan()
        Scanner.ioc.getLogger().getConfig().set('verbose', True, 'Logging')
        Scanner.ioc.getLogger().getConfig().set('trace', True, 'Logging')
        Scanner.ioc.getLogger().getConfig().set('config', 'full_stack_test', 'Sourcing')
        self.assertTrue(Scanner.execute({'loop': 1}))
        #############################################
        #            ASSERT SCANNING
        #############################################
        self.assertTrue(ioc.getCollection('SourceData').find_one({
            'grease_data.sourcing.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.detection.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.detection.start': None,
            'grease_data.detection.end': None
        }))
        #############################################
        #            EXECUTE DETECTION
        #############################################
        Detect = detect()
        Detect.ioc.getLogger().getConfig().set('verbose', True, 'Logging')
        Detect.ioc.getLogger().getConfig().set('trace', True, 'Logging')
        Detect.ioc.getLogger().getConfig().set('config', 'full_stack_test', 'Sourcing')
        self.assertTrue(Detect.execute({'loop': 1}))
        #############################################
        #            ASSERT DETECTION
        #############################################
        self.assertTrue(ioc.getCollection('SourceData').find_one({
            'grease_data.sourcing.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.detection.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.scheduling.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.scheduling.start': None,
            'grease_data.scheduling.end': None
        }))
        #############################################
        #            EXECUTE SCHEDULING
        #############################################
        Scheduling = schedule()
        Scheduling.ioc.getLogger().getConfig().set('verbose', True, 'Logging')
        Scheduling.ioc.getLogger().getConfig().set('trace', True, 'Logging')
        Scheduling.ioc.getLogger().getConfig().set('config', 'full_stack_test', 'Sourcing')
        self.assertTrue(Scheduling.execute({'loop': 1}))
        #############################################
        #            ASSERT SCHEDULING
        #############################################
        self.assertTrue(ioc.getCollection('SourceData').find_one({
            'grease_data.sourcing.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.detection.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.scheduling.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.execution.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.execution.start': None,
            'grease_data.execution.end': None
        }))
        #############################################
        #            EXECUTE JOBS
        #############################################
        ioc.getCollection('JobServer').update_one(
            {'_id': ObjectId(ioc.getConfig().NodeIdentity)},
            {
                '$set': {
                    'prototypes': []
                }
            }
        )
        Daemon = DaemonProcess(ioc)
        Daemon.ioc.getLogger().getConfig().set('verbose', True, 'Logging')
        Daemon.ioc.getLogger().getConfig().set('trace', True, 'Logging')
        Daemon.ioc.getLogger().getConfig().set('config', 'full_stack_test', 'Sourcing')
        self.assertTrue(Daemon.server())
        self.assertTrue(Daemon.drain_jobs(ioc.getCollection('SourceData')))
        #############################################
        #            ASSERT JOB EXECUTION
        #############################################
        # sleep a few for seconds to let help complete
        time.sleep(5)
        self.assertTrue(ioc.getCollection('SourceData').find_one({
            'grease_data.sourcing.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.detection.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.scheduling.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.execution.server': ObjectId(ioc.getConfig().NodeIdentity),
            'grease_data.execution.commandSuccess': True,
            'grease_data.execution.executionSuccess': True
        }))
        #############################################
        #            CLEAN UP TIME
        #############################################
        ioc.getCollection('JobServer').update_one(
            {'_id': ObjectId(ioc.getConfig().NodeIdentity)},
            {
                '$set': {
                    'prototypes': []
                }
            }
        )
        ioc.getCollection('Configuration').drop()
        ioc.getCollection('SourceData').drop()
        ioc.getCollection('DeDup_Sourcing').drop()
        pConf.load(reloadConf=True)
