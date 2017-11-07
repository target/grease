from tgt_grease.enterprise.Model import PrototypeConfig
from unittest import TestCase


class TestPrototypeConfig(TestCase):

    def test_type(self):
        conf = PrototypeConfig()
        self.assertTrue(isinstance(conf, object))
