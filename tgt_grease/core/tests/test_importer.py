from unittest import TestCase
from tgt_grease.core import ImportTool, Configuration, Logging


class TestImporter(TestCase):
    def test_load(self):
        log = Logging()
        imp = ImportTool(log)
        Conf = imp.load("Configuration")
        self.assertTrue(isinstance(Conf, Configuration))

    def test_failed_path(self):
        log = Logging()
        imp = ImportTool(log)
        obj = imp.load("defaultdict")
        self.assertFalse(obj)
