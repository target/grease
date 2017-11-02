import os
import json
import requests
from .BaseSourceClass import BaseSource
from tgt_grease_core_util import Configuration

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

class URLSource(BaseSource):
    def __init__(self):
        self._result = []
           
    def _dress_url(self, url):
        if 'http://' in url:
            return url
        if 'https://' in url:
            return url
        return 'http://' + url

    def _get_request(self, url):
        try:
            response = requests.get(url)
            return response
        except Exception as e:
            print e
            return -1

    def _get_peer(self, resp):
        #pull IP and port 
        resp = resp.raw._original_response
        if hasattr(resp, 'peer'):
            setattr(resp, 'host_ip', getattr(resp, 'peer')[0])
            setattr(resp, 'host_port', getattr(resp, 'peer')[1])
        else:
            setattr(resp, 'host_ip', '')
            setattr(resp, 'host_port', '')
        return resp

    def parse_source(self, rule_config):
        # type (dict) -> None
        # rule_config is an array of lists.
        for entry in rule_config:
            for url in entry['url']:
                dressed = self._dress_url(url)
                response = (self._get_request(dressed))
                peer = self._get_peer(response)

                #self._result needs to be an array of 1D lists.
                #looks like grease SourceDeDuplify encodes to JSON
                self._result.append({
                    'content': str(response.content),
                    'content_length': str(len(response.content)),
                    'elapsed': str(response.elapsed),
                    'headers': str(response.headers),
                    'response_host_ip': str(peer.host_ip),
                    'response_host_port': str(peer.host_port),
                    'status_code': str(response.status_code),
                    'url': str(url)
                })

    def get_records(self):
        # type: () -> dict
        return self._result

    def mock_data(self):
        # inherited
        pass

