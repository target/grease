from unittest import TestCase
from tgt_grease.core import Configuration
import os


class TestConfiguration(TestCase):
    def test_config_is_false_before_startup(self):
        self.assertFalse(Configuration.get('MongoDB', 'host'))

    def test_initialization(self):
        conf = Configuration()
        self.assertTrue(conf.get('Connectivity', 'MongoDB'))

    def test_filesystem(self):
        conf = Configuration()
        for elem in conf.FileSystem:
            self.assertTrue(os.path.isdir(conf.greaseDir + conf.fs_sep + elem))

    def test_defaults(self):
        conf = Configuration()
        self.assertEqual(conf.get('Connectivity', 'MongoDB').get('host'), 'localhost')
        self.assertEqual(conf.get('Connectivity', 'MongoDB').get('port'), 27017)
        self.assertEqual(conf.get('Logging', 'mode'), 'filesystem')
        self.assertEqual(conf.get('Logging', 'verbose'), False)
        self.assertEqual(conf.get('Logging', 'file'), conf.greaseDir + 'log' + conf.fs_sep + 'grease.log')
        self.assertEqual(conf.get('Configuration', 'mode'), 'filesystem')
        self.assertEqual(conf.get('Configuration', 'dir'), conf.greaseDir + 'etc' + conf.fs_sep)
        self.assertEqual(conf.get('Sourcing', 'mode'), 'filesystem')
        self.assertEqual(conf.get('Sourcing', 'dir'), conf.greaseDir + 'etc' + conf.fs_sep)
