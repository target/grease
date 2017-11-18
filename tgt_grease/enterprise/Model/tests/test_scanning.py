from unittest import TestCase
from tgt_grease.core import GreaseContainer, Configuration
from tgt_grease.enterprise.Model import Scan, PrototypeConfig, BaseSourceClass
from datetime import datetime
from bson.objectid import ObjectId
import json
import platform
import time
import uuid


class TestSource(BaseSourceClass):
    def parse_source(self, configuration):
        self._data = [
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': str(uuid.uuid4()),
                'field1': str(uuid.uuid4()),
                'field2': str(uuid.uuid4()),
                'field3': str(uuid.uuid4()),
                'field4': str(uuid.uuid4()),
                'field5': str(uuid.uuid4())
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': str(uuid.uuid4()),
                'field1': str(uuid.uuid4()),
                'field2': str(uuid.uuid4()),
                'field3': str(uuid.uuid4()),
                'field4': str(uuid.uuid4()),
                'field5': str(uuid.uuid4())
            },
            {
                'field': str(uuid.uuid4()),
                'field1': str(uuid.uuid4()),
                'field2': str(uuid.uuid4()),
                'field3': str(uuid.uuid4()),
                'field4': str(uuid.uuid4()),
                'field5': str(uuid.uuid4())
            },
            {
                'field': str(uuid.uuid4()),
                'field1': str(uuid.uuid4()),
                'field2': str(uuid.uuid4()),
                'field3': str(uuid.uuid4()),
                'field4': str(uuid.uuid4()),
                'field5': str(uuid.uuid4())
            }
        ]
        return True

    def mock_data(self, configuration):
        self._data = [
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': str(uuid.uuid4()),
                'field1': str(uuid.uuid4()),
                'field2': str(uuid.uuid4()),
                'field3': str(uuid.uuid4()),
                'field4': str(uuid.uuid4()),
                'field5': str(uuid.uuid4())
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': str(uuid.uuid4()),
                'field1': str(uuid.uuid4()),
                'field2': str(uuid.uuid4()),
                'field3': str(uuid.uuid4()),
                'field4': str(uuid.uuid4()),
                'field5': str(uuid.uuid4())
            },
            {
                'field': str(uuid.uuid4()),
                'field1': str(uuid.uuid4()),
                'field2': str(uuid.uuid4()),
                'field3': str(uuid.uuid4()),
                'field4': str(uuid.uuid4()),
                'field5': str(uuid.uuid4())
            },
            {
                'field': str(uuid.uuid4()),
                'field1': str(uuid.uuid4()),
                'field2': str(uuid.uuid4()),
                'field3': str(uuid.uuid4()),
                'field4': str(uuid.uuid4()),
                'field5': str(uuid.uuid4())
            }
        ]


class TestScan(TestCase):

    def test_scan(self):
        # setup
        configList = [
            {
                "name": "test1",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "TestSource",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ]
                }
            }
        ]
        ioc = GreaseContainer()
        ioc.ensureRegistration()
        ioc.getConfig().set('trace', True, 'Logging')
        ioc.getConfig().set('verbose', True, 'Logging')
        fil = open(ioc.getConfig().greaseConfigFile, 'r')
        data = json.loads(fil.read())
        fil.close()
        fil = open(ioc.getConfig().greaseConfigFile, 'w')
        data['Import']['searchPath'].append('tgt_grease.enterprise.Model.tests')
        fil.write(json.dumps(data, sort_keys=True, indent=4))
        fil.close()
        Configuration.ReloadConfig()
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

        # Begin Test
        conf = PrototypeConfig(ioc)
        conf.load(reloadConf=True, ConfigurationList=configList)
        scanner = Scan(ioc)
        # Scan Environment
        self.assertTrue(scanner.Parse())
        # Begin ensuring environment is how we expect
        # we assert less or equal because sometimes uuid's are close :p
        self.assertLessEqual(ioc.getCollection('SourceData').find({
            'detectionServer': ObjectId(jID1)
        }).count(), 3)
        self.assertLessEqual(ioc.getCollection('SourceData').find({
            'detectionServer': ObjectId(jID2)
        }).count(), 3)
        self.assertLessEqual(ioc.getCollection('JobServer').find_one({
            '_id': ObjectId(jID1)
        })['jobs'], 3)
        self.assertLessEqual(ioc.getCollection('JobServer').find_one({
            '_id': ObjectId(jID2)
        })['jobs'], 3)

        # clean up
        fil = open(ioc.getConfig().greaseConfigFile, 'r')
        data = json.loads(fil.read())
        fil.close()
        # remove collection
        ioc.getCollection('TestProtoType').drop()
        # remove prototypes
        data['NodeInformation']['ProtoTypes'] = []
        # pop search path
        trash = data['Import']['searchPath'].pop()
        # close out
        fil = open(ioc.getConfig().greaseConfigFile, 'w')
        fil.write(json.dumps(data, sort_keys=True, indent=4))
        fil.close()
        jServer.delete_one({'_id': ObjectId(jID1)})
        jServer.delete_one({'_id': ObjectId(jID2)})
        ioc.getCollection('SourceData').drop()
        ioc.getCollection('Dedup_Sourcing').drop()
        ioc.getConfig().set('trace', False, 'Logging')
        ioc.getConfig().set('verbose', False, 'Logging')
        Configuration.ReloadConfig()

    def test_config_load_empty(self):
        scan = Scan()
        confs = scan.generate_config_set()
        self.assertTrue(len(confs) == 0)
        self.assertTrue(isinstance(confs, list))

    def test_config_load_all(self):
        conf = PrototypeConfig()
        scan = Scan(conf.ioc)
        conf.load(reloadConf=True)
        configList = [
            {
                "name": "test1",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ]
                }
            },
            {
                "name": "test2",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "Google",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ]
                }
            },
            {
                "name": "test3",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "stackOverflow",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ],
                    "exists": [
                        {
                            "field": "var"
                        }
                    ]
                }
            }
        ]
        self.assertTrue(isinstance(conf.load(ConfigurationList=configList), dict))
        configs = scan.generate_config_set()
        self.assertTrue(isinstance(configs, list))
        self.assertTrue(len(configs) == len(configList))
        conf.load(reloadConf=True)

    def test_config_load_source(self):
        conf = PrototypeConfig()
        scan = Scan(conf.ioc)
        conf.load(reloadConf=True)
        configList = [
            {
                "name": "test1",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ]
                }
            },
            {
                "name": "test2",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "Google",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ]
                }
            },
            {
                "name": "test3",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "stackOverflow",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ],
                    "exists": [
                        {
                            "field": "var"
                        }
                    ]
                }
            }
        ]
        self.assertTrue(isinstance(conf.load(ConfigurationList=configList), dict))
        configs = scan.generate_config_set(source='Google')
        self.assertTrue(isinstance(configs, list))
        self.assertTrue(len(configs) == 1)
        conf.load(reloadConf=True)

    def test_config_load_name(self):
        conf = PrototypeConfig()
        scan = Scan(conf.ioc)
        conf.load(reloadConf=True)
        configList = [
            {
                "name": "test1",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ]
                }
            },
            {
                "name": "test2",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "Google",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ]
                }
            },
            {
                "name": "test3",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "stackOverflow",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ],
                    "exists": [
                        {
                            "field": "var"
                        }
                    ]
                }
            }
        ]
        self.assertTrue(isinstance(conf.load(ConfigurationList=configList), dict))
        configs = scan.generate_config_set(config='test1')
        self.assertTrue(isinstance(configs, list))
        self.assertTrue(len(configs) == 1)
        conf.load(reloadConf=True)

    def test_config_load_source_and_name(self):
        conf = PrototypeConfig()
        scan = Scan(conf.ioc)
        conf.load(reloadConf=True)
        configList = [
            {
                "name": "test1",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ]
                }
            },
            {
                "name": "test2",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "Google",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ]
                }
            },
            {
                "name": "test3",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "stackOverflow",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ],
                    "exists": [
                        {
                            "field": "var"
                        }
                    ]
                }
            }
        ]
        self.assertTrue(isinstance(conf.load(ConfigurationList=configList), dict))
        configs = scan.generate_config_set(config='test1', source='swapi')
        self.assertTrue(isinstance(configs, list))
        self.assertTrue(len(configs) == 1)
        conf.load(reloadConf=True)

    def test_config_load_bad_source_good_name(self):
        conf = PrototypeConfig()
        scan = Scan(conf.ioc)
        conf.load(reloadConf=True)
        configList = [
            {
                "name": "test1",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ]
                }
            },
            {
                "name": "test2",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "Google",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ]
                }
            },
            {
                "name": "test3",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "stackOverflow",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ],
                    "exists": [
                        {
                            "field": "var"
                        }
                    ]
                }
            }
        ]
        self.assertTrue(isinstance(conf.load(ConfigurationList=configList), dict))
        configs = scan.generate_config_set(config='test1', source='Google')
        self.assertTrue(isinstance(configs, list))
        self.assertTrue(len(configs) == 0)
        conf.load(reloadConf=True)

    def test_config_load_good_source_bad_name(self):
        conf = PrototypeConfig()
        scan = Scan(conf.ioc)
        conf.load(reloadConf=True)
        configList = [
            {
                "name": "test1",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ]
                }
            },
            {
                "name": "test2",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "Google",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ]
                }
            },
            {
                "name": "test3",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "stackOverflow",
                "logic": {
                    "regex": [
                        {
                            "field": "character",
                            "pattern": ".*skywalker.*"
                        }
                    ],
                    "exists": [
                        {
                            "field": "var"
                        }
                    ]
                }
            }
        ]
        self.assertTrue(isinstance(conf.load(ConfigurationList=configList), dict))
        configs = scan.generate_config_set(config='test7', source='swapi')
        self.assertTrue(isinstance(configs, list))
        self.assertTrue(len(configs) == 0)
        conf.load(reloadConf=True)
