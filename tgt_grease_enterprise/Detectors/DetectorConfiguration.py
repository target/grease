import os
import fnmatch
import json
import pkg_resources


class ConfigurationLoader(object):
    def __init__(self):
        self._raw_config = list()
        self._config_as_detectors = dict()
        self._scanners = list()
        self._load_config()

    def get_raw_config(self):
        # type: () -> list
        return self._raw_config

    def count_loaded_configurations(self):
        # type: () -> int
        return len(self.get_raw_config())

    def get_config_as_detectors(self):
        # type: () -> dict
        return self._config_as_detectors

    def get_scanners(self):
        # type: () -> list
        return self._scanners

    def get_scanner_config(self, detector_name):
        # type: (str) -> list
        if detector_name in self.get_config_as_detectors():
            return self.get_config_as_detectors()[detector_name]
        else:
            return list()

    def get_config(self, config_name):
        for conf in self.get_raw_config():
            if conf['name'] == config_name:
                return conf
        return {}

    def _load_config(self):
        # type: () -> None
        intermediate = list()
        dir_struct = pkg_resources.resource_filename(
            os.getenv('GREASE_CONF_PKG', ''),  os.getenv('GREASE_CONF_DIR', '') + '/'
        )
        matches = []
        for root, dirnames, filenames in os.walk(dir_struct):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                matches.append(os.path.join(root, filename))
        result = matches
        for doc in result:
            with open(doc) as current_file:
                content = current_file.read().replace('\r\n', '')
            try:
                intermediate.append(json.loads(content))
            except ValueError:
                continue
        self._raw_config = intermediate
        result = {}
        for conf in self.get_raw_config():
            if conf['detector'] not in result:
                result[conf['detector']] = list()
            result[conf['detector']].append(conf)
        self._config_as_detectors = result
        result = list()
        for scanner, data in self.get_config_as_detectors().iteritems():
            result.append(scanner)
        self._scanners = result
        del result
