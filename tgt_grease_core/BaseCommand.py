from abc import ABCMeta, abstractmethod
from tgt_grease_core_util.GreaseUtility import Grease
import time


class GreaseCommand(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.purpose = "Abstract Base Class"
        self._machines_effected = 0
        self._start_time = time.time()
        self._ioc = Grease()

    def __del__(self):
        self._ioc.__del__()

    def set_effected(self, count):
        # type: (int) -> None
        self._machines_effected = int(count)

    def get_effected(self):
        # type: () -> int
        return int(self._machines_effected)

    def get_start_time(self):
        # type: () -> float
        return float(self._start_time)

    @abstractmethod
    def execute(self):
        """execute should be the primary logic for your execution"""
        pass
