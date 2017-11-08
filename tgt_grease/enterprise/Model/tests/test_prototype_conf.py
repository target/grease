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
