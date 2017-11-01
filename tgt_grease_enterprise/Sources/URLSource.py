import os
import json
from .BaseSourceClass import BaseSource
from tgt_grease_core_util import Configuration


class URLSource(BaseSource):
    def __init__(self):
        print('newing up URLSource')
        self._result = {}

    def _get_online(self, host):
        if os.name == 'nt':
            parameters = "-n 1"
        else:
            parameters = "-q -c 1"

        call = "ping " + parameters + " " + host
        print call
        return os.system(call)

    def mock_data(self):
        #inherited
        pass

    def parse_source(self, rule_config):
        # type (dict) -> None
        strip_header = json.loads(rule_config)['URLSource'][0]

        for url in strip_header['url']:
            continue
            #self._result.append(self._get_online(url))


    def get_records(self):
        # type: () -> dict
        return self._result

