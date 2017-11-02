import os
import json
import requests
import time
from .BaseSourceClass import BaseSource
from tgt_grease_core_util import Configuration


class URLSource(BaseSource):
    def __init__(self):
        self._result = []

        # Overwrite getresponse, so it saves host ip/port
        import httplib
        def getresponse(self, *args, **kwargs):
            response = self._old_getresponse(*args, **kwargs)
            if self.sock:
                response.peer = self.sock.getpeername()
            else:
                response.peer = None
            return response

        httplib.HTTPConnection._old_getresponse =\
                httplib.HTTPConnection.getresponse
        httplib.HTTPConnection.getresponse = getresponse

    def _dress_url(self, url):
        return 'http://' + url

    def _get_request(self, url):
        try:
            response = requests.get(url)
            return response
        except Exception as e:
            print e
            return -1

    def parse_source(self, rule_config):
        # type (dict) -> None
        # rule_config is an array of lists.
        for entry in rule_config['URLSource']:
            for url in entry['url']:
                dressed = self._dress_url(url)
                response = (self._get_request(dressed))

                #pull IP and port 
                orig = response.raw._original_response
                if hasattr(orig, 'peer'):
                    response_host_ip = str(getattr(orig, 'peer')[0])
                    response_host_port = str(getattr(orig, 'peer')[1])
                else:
                    response_host_ip = ''
                    response_host_port = ''

                #self._result needs to be an array of 1D lists.
                self._result.append({
                    'content': response.content,
                    'content_length': len(response.content),
                    'elapsed': response.elapsed,
                    'headers': response.headers,
                    'response_host_ip': response_host_ip,
                    'response_host_port': response_host_port,
                    'status_code': response.status_code,
                    'url': url
                })

    def get_records(self):
        # type: () -> dict
        return self._result

    def mock_data(self):
        # inherited
        pass


