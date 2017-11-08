from tgt_grease.enterprise.Model import PrototypeConfig
from tgt_grease.core import GreaseContainer
from unittest import TestCase
import json
import fnmatch
import os


class TestPrototypeConfig(TestCase):

    def __init__(self):
        super(TestPrototypeConfig, self).__init__()
        c = GreaseContainer()
        c.getConfig().set('trace', True, 'Logging')
        del c

    def test_type(self):
        conf = PrototypeConfig()
        self.assertTrue(isinstance(conf, object))

    def test_empty_conf(self):
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
                'sources': ['swapi']
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
                'sources': ['swapi']
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
        self.assertDictEqual(
            {
                'raw': configList,
                'configuration': {
                    'fs': configList,
                    'mongo': [],
                    'pkg': []
                },
                'source': {
                    'swapi': [
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
                        }
                    ],
                    'Google': [
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
                    ],
                    'stackOverflow': [
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
                        }
                    ]
                },
                'sources': ['swapi', 'stackOverflow', 'Google']
            },
            conf.getConfiguration()
        )
        self.assertEqual(['swapi', 'stackOverflow', 'Google'], conf.get_sources())
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
        self.assertDictEqual(
            {
                'raw': GoodConfigList,
                'configuration': {
                    'fs': GoodConfigList,
                    'mongo': [],
                    'pkg': []
                },
                'source': {
                    'swapi': [
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
                        }
                    ],
                    'Google': [
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
                },
                'sources': ['swapi', 'Google']
            },
            conf.getConfiguration()
        )
        self.assertEqual(['swapi', 'Google'], conf.get_sources())
        # clean up
        for root, dirnames, filenames in os.walk(ioc.getConfig().get('Configuration', 'dir')):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                self.assertIsNone(os.remove(os.path.join(root, filename)))
        # clear the config
        conf.load(reloadConf=True)
