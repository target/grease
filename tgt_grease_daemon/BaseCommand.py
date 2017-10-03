from abc import ABCMeta, abstractmethod
import time
import os
import threading
import sys
from tgt_grease_core.BaseCommand import GreaseCommand


class GreaseDaemonCommand(GreaseCommand):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(GreaseDaemonCommand, self).__init__()
        self.purpose = "Abstract Base Class"
        self._machines_effected = 0
        self._start_time = time.time()
        if os.name == 'nt':
            self._identity_file = "C:\\grease\\grease_identity.txt"
        else:
            self._identity_file = "/tmp/grease/grease_identity.txt"
        if os.path.isfile(self._identity_file):
            self._grease_identity = open(self._identity_file, 'r').read().rstrip()
        else:
            self._grease_identity = ''
        self.exe_state = {
            'execution': False,
            'result': False,
            'isDaemon': True
        }

    def set_effected(self, count):
        # type: (int) -> None
        self._machines_effected = int(count)

    def get_effected(self):
        # type: () -> int
        return int(self._machines_effected)

    def get_start_time(self):
        # type: () -> float
        return float(self._start_time)

    def attempt_execution(self, command_id, context='{}'):
        # type: (int, dict) -> None
        self.set_exe_state('command_id', int(command_id))
        try:
            self.set_exe_state('result', bool(self.execute(context)))
            self.set_exe_state('execution', True)
        except:
            self._ioc.message().error("Command Execution Failed! Exception Raised: [{0}]".format(str(sys.exc_info())))
            return
        return

    def get_exe_state(self):
        # type: () -> dict
        return self.exe_state

    def set_exe_state(self, key, value):
        # type: (str, object) -> None
        self.exe_state[key] = value

    @abstractmethod
    def execute(self, context='{}'):
        # type: (list) -> bool
        """execute should be the primary logic for your execution"""
        pass
