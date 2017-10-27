from abc import ABCMeta, abstractmethod
import json
import os
import fnmatch
from tgt_grease_core_util import Configuration


class BaseSource(object):
    __metaclass__ = ABCMeta

    composite_score_strength_limit = None

    def mock_data(self):
        # type: () -> list
        conf = Configuration()
        matches = []
        final = []
        for root, dirnames, filenames in os.walk(conf.opt_dir):
            for filename in fnmatch.filter(filenames, '*.mock.{0}.json'.format(self.__class__.__name__)):
                matches.append(os.path.join(root, filename))
        for doc in matches:
            with open(doc) as current_file:
                content = current_file.read().replace('\r\n', '')
            try:
                for res in json.loads(content):
                    final.append(res)
            except ValueError:
                continue
        return final

    @abstractmethod
    def parse_source(self, rule_config):
        # type (dict) -> None
        pass

    @abstractmethod
    def get_records(self):
        # type: () -> dict
        pass

    def duplicate_check_fields(self):
        # type: () -> list
        return []
