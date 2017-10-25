import os
from tgt_grease_core_util import Configuration
from tgt_grease_enterprise import BaseSource


class URLSource(BaseSource):
    def __init__(self):
        self._result = {}

    def _get_online(self, host):
        if os.name == 'nt':
            parameters = "-n 1"
        else:
            parameters = "-c 1"

        call = "ping " + parameters + " " + host
        print call
        return os.system(call)

    def mock_data(self):
        #inherited
        pass

    def parse_source(self, rule_config):
        # type (dict) -> None
        print "IN parse_source"
        print rule_config
        hosts = rule_config[0]['hosts']
        for host in hosts:
            print self._get_online(host)
        #Iterate over a list of IP addresses to ping.
        #Iterate over a list of hostnames to ping.
        #Iterate over a list of API endpoints to hit.
        #Return a dict

    def get_records(self):
        # type: () -> dict
        return self._result

