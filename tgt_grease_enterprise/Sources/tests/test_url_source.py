from unittest import TestCase
from tgt_grease_enterprise.Sources import URLSource, BaseSource


class TestURLSource(TestCase):
    def _setup(self):
        self.URLSource = URLSource()

    def _teardown(self):
        print('doing nothing')

    def test_source_is_source(self):
        self._setup()
        self.assertTrue(isinstance(self.URLSource, BaseSource))

