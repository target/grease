import os
import json
import requests
import time
from .BaseSourceClass import BaseSource
from tgt_grease_core_util import Configuration


class URLSource(BaseSource):
    def __init__(self):
        self._result = {}

    def _dress_url(self, url):
        return 'http://' + url

    def _get_request(self, url):
        try:
            return requests.get(url)
        except:
            return -1

    def mock_data(self):
        #inherited
        pass

    def parse_source(self, rule_config):
        # type (dict) -> None
        for entry in rule_config['URLSource']:
            for url in entry['url']:
                dressed = self._dress_url(url)
                response = (self._get_request(dressed))
                self._result[url] = {}
                self._result[url]['url'] = response.url
                #self._result[url]['text'] = response.text
                self._result[url]['elapsed'] = response.elapsed
                self._result[url]['encoding'] = response.encoding
                self._result[url]['headers'] = response.headers
                self._result[url]['status_code'] = response.status_code

    def get_records(self):
        # type: () -> dict
        return self._result

