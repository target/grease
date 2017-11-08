from tgt_grease.enterprise.Model import PrototypeConfig
from unittest import TestCase


class TestPrototypeConfig(TestCase):

    def test_type(self):
        conf = PrototypeConfig()
        self.assertTrue(isinstance(conf, object))

    def test_empty_conf(self):
        conf = PrototypeConfig()
        self.assertTrue(conf.getConfiguration())
        self.assertListEqual(conf.getConfiguration().get('configuration').get('pkg'), [])
        self.assertListEqual(conf.getConfiguration().get('configuration').get('fs'), [])
        self.assertListEqual(conf.getConfiguration().get('configuration').get('mongo'), [])

    def test_validation_list_good(self):
        conf = PrototypeConfig()
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

    def test_validation_list_bad(self):
        conf = PrototypeConfig()
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
