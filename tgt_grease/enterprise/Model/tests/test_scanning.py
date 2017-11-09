from unittest import TestCase
from tgt_grease.enterprise.Model import Scan, PrototypeConfig


class TestScan(TestCase):

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
