from tgt_grease.enterprise.Model import PrototypeConfig
from tgt_grease.core import GreaseContainer
from unittest import TestCase
import json
import fnmatch
import os
import time
import pkg_resources


class TestPrototypeConfig(TestCase):

    def test_type(self):
        conf = PrototypeConfig()
        self.assertTrue(isinstance(conf, object))

    def test_empty_conf(self):
        ioc = GreaseContainer()
        # clean up
        for root, dirnames, filenames in os.walk(ioc.getConfig().get('Configuration', 'dir')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
        conf = PrototypeConfig()
        conf.load(reloadConf=True)
        self.assertTrue(conf.getConfiguration())
        self.assertListEqual(conf.getConfiguration().get('configuration').get('pkg'), [])
        self.assertListEqual(conf.getConfiguration().get('configuration').get('fs'), [])
        self.assertListEqual(conf.getConfiguration().get('configuration').get('mongo'), [])
        conf.load(reloadConf=True)

    def test_validation_list_good(self):
        conf = PrototypeConfig()
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
                "name": "test3",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
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
        self.assertEqual(configList, conf.validate_config_list(configList))
        conf.load(reloadConf=True)

    def test_validation_list_bad(self):
        conf = PrototypeConfig()
        conf.load(reloadConf=True)
        configList = [
            {
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
                "logic": {}
            },
            {
                "name": "test1",
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
            },
            {
                "name": "test3",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
                "logic": []
            },
            {
                "name": "test4",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
                "logic": {

                }
            },
            {
                "name": "test5",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
                "logic": {
                    "regex": [
                        {
                            "field": "var",
                            "pattern": "ver.*"
                        }
                    ]
                }
            }
        ]
        CompareList = [
            {
                "name": "test5",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
                "logic": {
                    "regex": [
                        {
                            "field": "var",
                            "pattern": "ver.*"
                        }
                    ]
                }
            }
        ]
        self.assertEqual(CompareList, conf.validate_config_list(configList))
        conf.load(reloadConf=True)

    def test_validation_good(self):
        test = {
            "name": "test5",
            "job": "fakeJob",
            "exe_env": "windows",
            "source": "swapi",
            "logic": {
                "regex": [
                    {
                        "field": "var",
                        "pattern": "ver.*"
                    }
                ]
            }
        }
        conf = PrototypeConfig()
        self.assertTrue(conf.validate_config(test))

    def test_validation_bad(self):
        conf = PrototypeConfig()
        test = {
            "name": "test1",
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
        }
        self.assertFalse(conf.validate_config(test))
        test1 = {
            "name": "test2",
            "job": "fakeJob",
            "exe_env": "windows",
        }
        self.assertFalse(conf.validate_config(test1))
        test2 = {
            "name": "test3",
            "job": "fakeJob",
            "exe_env": "windows",
            "source": "swapi",
            "logic": []
        }
        self.assertFalse(conf.validate_config(test2))
        test3 = {
            "name": "test4",
            "job": "fakeJob",
            "exe_env": "windows",
            "source": "swapi",
            "logic": {

            }
        }
        self.assertFalse(conf.validate_config(test3))

    def test_load_good(self):
        conf = PrototypeConfig()
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
                "name": "test3",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
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
        self.assertDictEqual(
            {
                'raw': configList,
                'configuration': {
                    'ConfigurationList': configList
                },
                'source': {
                    'swapi': configList,
                },
                'sources': ['swapi'],
                'names': ['test1', 'test2', 'test3'],
                'name': {
                    'test1': configList[0],
                    'test2': configList[1],
                    'test3': configList[2]
                }
            },
            conf.load(ConfigurationList=configList)
        )
        conf.load(reloadConf=True)

    def test_load_bad(self):
        conf = PrototypeConfig()
        conf.load(reloadConf=True)
        configList = [
            {
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
                "logic": {}
            },
            {
                "name": "test1",
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
            },
            {
                "name": "test3",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
                "logic": []
            },
            {
                "name": "test4",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
                "logic": {

                }
            },
            {
                "name": "test5",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
                "logic": {
                    "regex": [
                        {
                            "field": "var",
                            "pattern": "ver.*"
                        }
                    ]
                }
            }
        ]
        CompareList = [
            {
                "name": "test5",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
                "logic": {
                    "regex": [
                        {
                            "field": "var",
                            "pattern": "ver.*"
                        }
                    ]
                }
            }
        ]
        self.assertDictEqual(
            {
                'raw': CompareList,
                'configuration': {
                    'ConfigurationList': CompareList
                },
                'source': {
                    'swapi': CompareList
                },
                'sources': ['swapi'],
                'names': ['test5'],
                'name': {
                    'test5': CompareList[0]
                }
            },
            conf.load(ConfigurationList=configList)
        )
        conf.load(reloadConf=True)

    def test_get_sources_all_good(self):
        conf = PrototypeConfig()
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
                "source": "stackOverflow",
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
                "source": "Google",
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
        conf.load(ConfigurationList=configList)
        self.assertEqual(['swapi', 'stackOverflow', 'Google'], conf.get_sources())
        conf.load(reloadConf=True)

    def test_get_sources_bad(self):
        conf = PrototypeConfig()
        conf.load(reloadConf=True)
        configList = [
            {
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "swapi",
                "logic": {}
            },
            {
                "name": "test1",
                "exe_env": "windows",
                "source": "stackOverflow",
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
            },
            {
                "name": "test3",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "Google",
                "logic": []
            },
            {
                "name": "test4",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "CarlBurger",
                "logic": {

                }
            },
            {
                "name": "test5",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "slack",
                "logic": {
                    "regex": [
                        {
                            "field": "var",
                            "pattern": "ver.*"
                        }
                    ]
                }
            }
        ]
        conf.load(ConfigurationList=configList)
        self.assertEqual(['slack'], conf.get_sources())
        conf.load(reloadConf=True)

    def test_fs_load_good(self):
        ioc = GreaseContainer()
        # clean up
        for root, dirnames, filenames in os.walk(ioc.getConfig().get('Configuration', 'dir')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
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
                "source": "stackOverflow",
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
                "source": "Google",
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
        i = 0
        for conf in configList:
            with open(ioc.getConfig().get('Configuration', 'dir') + 'conf{0}.config.json'.format(i), 'w') as fil:
                fil.write(json.dumps(conf, indent=4))
            i += 1
        conf = PrototypeConfig(ioc)
        conf.load(reloadConf=True)
        self.assertEqual(len(conf.getConfiguration().get('configuration').get('fs')), len(configList))
        self.assertEqual(len(conf.getConfiguration().get('raw')), len(configList))
        self.assertEqual(len(conf.getConfiguration().get('source').get('swapi')), 1)
        self.assertEqual(len(conf.getConfiguration().get('source').get('stackOverflow')), 1)
        self.assertEqual(len(conf.getConfiguration().get('source').get('Google')), 1)
        self.assertEqual(3, len(conf.get_sources()))
        self.assertEqual(3, len(conf.get_names()))
        self.assertEqual(len(conf.get_source('stackOverflow')), 1)
        self.assertTrue(isinstance(conf.get_config('test2'), dict))
        self.assertTrue(conf.get_config('test2'))
        # clean up
        for root, dirnames, filenames in os.walk(ioc.getConfig().get('Configuration', 'dir')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
        # clear the config
        conf.load(reloadConf=True)

    def test_fs_load_bad(self):
        ioc = GreaseContainer()
        # clean up
        for root, dirnames, filenames in os.walk(ioc.getConfig().get('Configuration', 'dir')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
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
                "name": "badtest1",
                "exe_env": "windows",
                "source": "stackOverflow",
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
                "source": "Google",
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
        GoodConfigList = [
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
                "name": "test3",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "Google",
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
        i = 0
        for conf in configList:
            with open(ioc.getConfig().get('Configuration', 'dir') + 'conf{0}.config.json'.format(i), 'w') as fil:
                fil.write(json.dumps(conf, indent=4))
            i += 1
        conf = PrototypeConfig(ioc)
        conf.load(reloadConf=True)
        self.assertEqual(len(conf.getConfiguration().get('configuration').get('fs')), len(GoodConfigList))
        self.assertEqual(len(conf.getConfiguration().get('raw')), len(GoodConfigList))
        self.assertEqual(len(conf.getConfiguration().get('source').get('swapi')), 1)
        self.assertEqual(len(conf.getConfiguration().get('source').get('Google')), 1)
        self.assertEqual(2, len(conf.get_sources()))
        self.assertEqual(2, len(conf.get_names()))
        self.assertEqual(len(conf.get_source('Google')), 1)
        self.assertTrue(isinstance(conf.get_config('test1'), dict))
        self.assertTrue(conf.get_config('test1'))
        # clean up
        for root, dirnames, filenames in os.walk(ioc.getConfig().get('Configuration', 'dir')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
        # clear the config
        conf.load(reloadConf=True)

    def test_pkg_load_good(self):
        ioc = GreaseContainer()
        # clean up
        for root, dirnames, filenames in os.walk(pkg_resources.resource_filename('tgt_grease.enterprise.Model', 'config/')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
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
                "source": "stackOverflow",
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
                "source": "Google",
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
        i = 0
        for conf in configList:
            with open(pkg_resources.resource_filename('tgt_grease.enterprise.Model', 'config/') + 'conf{0}.config.json'.format(i), 'w') as fil:
                fil.write(json.dumps(conf, indent=4))
            i += 1
        conf = PrototypeConfig(ioc)
        conf.load(reloadConf=True)
        self.assertEqual(len(conf.getConfiguration().get('configuration').get('pkg')), len(configList))
        self.assertEqual(len(conf.getConfiguration().get('raw')), len(configList))
        self.assertEqual(len(conf.getConfiguration().get('source').get('swapi')), 1)
        self.assertEqual(len(conf.getConfiguration().get('source').get('stackOverflow')), 1)
        self.assertEqual(len(conf.getConfiguration().get('source').get('Google')), 1)
        self.assertEqual(3, len(conf.get_sources()))
        self.assertEqual(3, len(conf.get_names()))
        self.assertEqual(len(conf.get_source('stackOverflow')), 1)
        self.assertTrue(isinstance(conf.get_config('test2'), dict))
        self.assertTrue(conf.get_config('test2'))
        # clean up
        for root, dirnames, filenames in os.walk(pkg_resources.resource_filename('tgt_grease.enterprise.Model', 'config/')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
        # clear the config
        conf.load(reloadConf=True)

    def test_pkg_load_bad(self):
        ioc = GreaseContainer()
        # clean up
        for root, dirnames, filenames in os.walk(pkg_resources.resource_filename('tgt_grease.enterprise.Model', 'config/')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
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
                "name": "badtest1",
                "exe_env": "windows",
                "source": "stackOverflow",
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
                "source": "Google",
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
        GoodConfigList = [
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
                "name": "test3",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "Google",
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
        i = 0
        for conf in configList:
            with open(pkg_resources.resource_filename('tgt_grease.enterprise.Model', 'config/') + 'conf{0}.config.json'.format(i), 'w') as fil:
                fil.write(json.dumps(conf, indent=4))
            i += 1
        conf = PrototypeConfig(ioc)
        conf.load(reloadConf=True)
        self.assertEqual(len(conf.getConfiguration().get('configuration').get('pkg')), len(GoodConfigList))
        self.assertEqual(len(conf.getConfiguration().get('raw')), len(GoodConfigList))
        self.assertEqual(len(conf.getConfiguration().get('source').get('swapi')), 1)
        self.assertEqual(len(conf.getConfiguration().get('source').get('Google')), 1)
        self.assertEqual(2, len(conf.get_sources()))
        self.assertEqual(2, len(conf.get_names()))
        self.assertEqual(len(conf.get_source('Google')), 1)
        self.assertTrue(isinstance(conf.get_config('test1'), dict))
        self.assertTrue(conf.get_config('test1'))
        # clean up
        for root, dirnames, filenames in os.walk(pkg_resources.resource_filename('tgt_grease.enterprise.Model', 'config/')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
        # clear the config
        conf.load(reloadConf=True)

    def test_mongo_load_good(self):
        ioc = GreaseContainer()
        # clean up
        for root, dirnames, filenames in os.walk(ioc.getConfig().get('Configuration', 'dir')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
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
                "source": "stackOverflow",
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
                "source": "Google",
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
        for conf in configList:
            ioc.getCollection('Configuration').insert_one(conf)
        ioc.getCollection('Configuration').update_many({}, {'$set': {'active': True, 'type': 'prototype_config'}})
        # sleep because travis is slow
        time.sleep(1.5)
        conf = PrototypeConfig(ioc)
        conf.load(reloadConf=True)
        self.assertEqual(len(conf.getConfiguration().get('configuration').get('mongo')), len(configList))
        self.assertEqual(len(conf.getConfiguration().get('raw')), len(configList))
        self.assertEqual(len(conf.getConfiguration().get('source').get('swapi')), 1)
        self.assertEqual(len(conf.getConfiguration().get('source').get('stackOverflow')), 1)
        self.assertEqual(len(conf.getConfiguration().get('source').get('Google')), 1)
        self.assertEqual(3, len(conf.get_names()))
        self.assertEqual(len(conf.get_source('stackOverflow')), 1)
        self.assertTrue(isinstance(conf.get_config('test2'), dict))
        self.assertTrue(conf.get_config('test2'))
        # clean up
        ioc.getCollection('Configuration').drop()
        # clear the config
        conf.load(reloadConf=True)

    def test_mongo_load_bad(self):
        ioc = GreaseContainer()
        # clean up
        for root, dirnames, filenames in os.walk(ioc.getConfig().get('Configuration', 'dir')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
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
                "name": "badtest1",
                "exe_env": "windows",
                "source": "stackOverflow",
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
                "source": "Google",
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
        GoodConfigList = [
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
                "name": "test3",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "Google",
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
        for conf in configList:
            ioc.getCollection('Configuration').insert_one(conf)
        ioc.getCollection('Configuration').update_many({}, {'$set': {'active': True, 'type': 'prototype_config'}})
        # sleep because travis is slow sometimes
        time.sleep(1.5)
        conf = PrototypeConfig(ioc)
        conf.load(reloadConf=True)
        self.assertEqual(len(conf.getConfiguration().get('configuration').get('mongo')), len(GoodConfigList))
        self.assertEqual(len(conf.getConfiguration().get('raw')), len(GoodConfigList))
        self.assertEqual(len(conf.getConfiguration().get('source').get('swapi')), 1)
        self.assertEqual(len(conf.getConfiguration().get('source').get('Google')), 1)
        self.assertEqual(2, len(conf.get_sources()))
        self.assertEqual(2, len(conf.get_names()))
        self.assertEqual(len(conf.get_source('Google')), 1)
        self.assertTrue(isinstance(conf.get_config('test1'), dict))
        self.assertTrue(conf.get_config('test1'))
        # clean up
        ioc.getCollection('Configuration').drop()
        # clear the config
        conf.load(reloadConf=True)

    def test_all_load_good(self):
        ioc = GreaseContainer()
        # clean up
        for root, dirnames, filenames in os.walk(ioc.getConfig().get('Configuration', 'dir')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
        # clean up
        for root, dirnames, filenames in os.walk(pkg_resources.resource_filename('tgt_grease.enterprise.Model', 'config/')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
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
                "source": "stackOverflow",
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
                "source": "Google",
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
        i = 0
        length = len(configList) - 1
        while i <= length:
            if i == 0:
                with open(ioc.getConfig().get('Configuration', 'dir') + 'conf{0}.config.json'.format(i), 'w') as fil:
                    fil.write(json.dumps(configList[i], indent=4))
            if i == 1:
                with open(pkg_resources.resource_filename('tgt_grease.enterprise.Model',
                                                          'config/') + 'conf{0}.config.json'.format(i), 'w') as fil:
                    fil.write(json.dumps(configList[i], indent=4))
            if i == 2:
                ioc.getCollection('Configuration').insert_one(configList[i])
            i += 1
        ioc.getCollection('Configuration').update_many({}, {'$set': {'active': True, 'type': 'prototype_config'}})
        # sleep because travis is slow
        time.sleep(1.5)
        conf = PrototypeConfig(ioc)
        conf.load(reloadConf=True)
        self.assertEqual(len(conf.getConfiguration().get('configuration').get('mongo')), 1)
        self.assertEqual(len(conf.getConfiguration().get('configuration').get('pkg')), 1)
        self.assertEqual(len(conf.getConfiguration().get('configuration').get('fs')), 1)
        self.assertEqual(len(conf.getConfiguration().get('raw')), len(configList))
        self.assertEqual(len(conf.getConfiguration().get('source').get('swapi')), 1)
        self.assertEqual(len(conf.getConfiguration().get('source').get('stackOverflow')), 1)
        self.assertEqual(len(conf.getConfiguration().get('source').get('Google')), 1)
        self.assertEqual(3, len(conf.get_names()))
        self.assertEqual(len(conf.get_source('stackOverflow')), 1)
        self.assertTrue(isinstance(conf.get_config('test2'), dict))
        self.assertTrue(conf.get_config('test2'))
        # clean up
        ioc.getCollection('Configuration').drop()
        for root, dirnames, filenames in os.walk(ioc.getConfig().get('Configuration', 'dir')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
        # clean up
        for root, dirnames, filenames in os.walk(pkg_resources.resource_filename('tgt_grease.enterprise.Model', 'config/')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
        # clear the config
        conf.load(reloadConf=True)

    def test_all_load_bad(self):
        ioc = GreaseContainer()
        # clean up
        for root, dirnames, filenames in os.walk(ioc.getConfig().get('Configuration', 'dir')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
        # clean up
        for root, dirnames, filenames in os.walk(pkg_resources.resource_filename('tgt_grease.enterprise.Model', 'config/')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
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
                "name": "badtest1",
                "exe_env": "windows",
                "source": "stackOverflow",
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
                "source": "Google",
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
        GoodConfigList = [
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
                "name": "test3",
                "job": "fakeJob",
                "exe_env": "windows",
                "source": "Google",
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
        i = 0
        length = len(configList) - 1
        while i <= length:
            if i == 0:
                with open(ioc.getConfig().get('Configuration', 'dir') + 'conf{0}.config.json'.format(i), 'w') as fil:
                    fil.write(json.dumps(configList[i], indent=4))
            if i == 1:
                with open(pkg_resources.resource_filename('tgt_grease.enterprise.Model',
                                                          'config/') + 'conf{0}.config.json'.format(i), 'w') as fil:
                    fil.write(json.dumps(configList[i], indent=4))
            if i == 2:
                ioc.getCollection('Configuration').insert_one(configList[i])
            i += 1
        ioc.getCollection('Configuration').update_many({}, {'$set': {'active': True, 'type': 'prototype_config'}})
        # sleep because travis is slow
        time.sleep(1.5)
        conf = PrototypeConfig(ioc)
        conf.load(reloadConf=True)
        self.assertEqual(len(conf.getConfiguration().get('configuration').get('mongo')), 1)
        self.assertEqual(len(conf.getConfiguration().get('configuration').get('pkg')), 0)
        self.assertEqual(len(conf.getConfiguration().get('configuration').get('fs')), 1)
        self.assertEqual(len(conf.getConfiguration().get('raw')), len(GoodConfigList))
        self.assertEqual(len(conf.getConfiguration().get('source').get('swapi')), 1)
        self.assertEqual(len(conf.getConfiguration().get('source').get('Google')), 1)
        self.assertEqual(2, len(conf.get_names()))
        self.assertEqual(len(conf.get_source('Google')), 1)
        self.assertTrue(isinstance(conf.get_config('test1'), dict))
        self.assertTrue(conf.get_config('test1'))
        # clean up
        ioc.getCollection('Configuration').drop()
        for root, dirnames, filenames in os.walk(ioc.getConfig().get('Configuration', 'dir')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
        # clean up
        for root, dirnames, filenames in os.walk(pkg_resources.resource_filename('tgt_grease.enterprise.Model', 'config/')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
        # clear the config
        conf.load(reloadConf=True)
