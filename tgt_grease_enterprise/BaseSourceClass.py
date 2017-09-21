from abc import ABCMeta, abstractmethod


class BaseSource(object):
    __metaclass__ = ABCMeta

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

