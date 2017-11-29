from unittest import TestCase
from tgt_grease_enterprise.Sources import URLSource, BaseSource


class TestURLSource(TestCase):
    def _setup(self):
        self.URLSource = URLSource()
        self._vanilla_url = 'www.google.com'
        self._protocol_url = 'http://www.google.com'
        self._final_url = 'http://www.google.com'
        self._secure_protocol_url = 'https://www.google.com'
        self._secure_final_url = 'https://www.google.com'

    def _teardown(self):
        pass

    def test_source_is_source(self):
        self._setup()
        self.assertTrue(isinstance(self.URLSource, BaseSource))

    def test_dress_vanilla_url(self):
        self._setup()
        self.assertEqual(
            self.URLSource._dress_url(self._vanilla_url),
            self._final_url
        )

    def test_dress_protocol_url(self):
        self._setup()
        self.assertEqual(
            self.URLSource._dress_url(self._protocol_url),
            self._final_url
        )
        self.assertEqual(
            self.URLSource._dress_url(self._secure_protocol_url),
            self._secure_final_url
        )

    def test_get_peer(self):
        self._setup()
        #How can I generate a response object?

