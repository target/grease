from tgt_grease.enterprise.Model import PrototypeConfig
from unittest import TestCase


class TestPrototypeConfig(TestCase):

    def test_type(self):
        conf = PrototypeConfig()
        self.assertTrue(isinstance(conf, object))

    def test_empty_conf(self):
        conf = PrototypeConfig()
        self.assertTrue(conf.Configuration)
        self.assertListEqual(conf.Configuration.get('configuration').get('pkg'), [])
        self.assertListEqual(conf.Configuration.get('configuration').get('fs'), [])
        self.assertListEqual(conf.Configuration.get('configuration').get('mongo'), [])
