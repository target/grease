from abc import ABCMeta, abstractmethod


class BaseDetector(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def param_compute(self, source, rules):
        # type: (dict, dict) -> None
        pass

    @abstractmethod
    def get_result(self):
        # type: () -> dict
        pass
