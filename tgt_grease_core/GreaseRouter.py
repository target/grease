import sys
import time
from collections import deque
from tgt_grease_core.BaseCommand import GreaseCommand
from tgt_grease_core_util import Grease
from tgt_grease_core_util.ImportTools import Importer


class Router(object):
    """class Router handles routing requests to grease utilities"""
    def __init__(self):
        self.start_time = time.time()
        self.args = deque(sys.argv)
        # Pop the entrypoint off the stack
        self.args.popleft()
        self._grease = Grease()
        self._importer = Importer(self._grease.message())

    @staticmethod
    def entry_point():
        """entry_point is the 'main' method of the core system"""
        router = Router()
        router.gateway()

    def gateway(self):
        """gateway is the top level routing method for parsing commands"""
        if len(self.args) >= 2:
            instance = self._importer.load(self.args[0], self.args[1])
            if isinstance(instance, GreaseCommand):
                return_state = bool(instance.execute())
                Grease.run_telemetry(instance, return_state)
                if return_state:
                    self._grease.message().debug('Grease Request Successful::' + str(list(self.args)))
                    sys.exit(0)
                else:
                    self._grease.message().error('Grease Request Failed::' + str(list(self.args)))
                    self.bad_exit("Process Failed", 6)
            else:
                self.bad_exit("Loaded Command Does Not Implement GreaseCommand :: This is a development issue please "
                              "contact owner", 5)
        else:
            if len(self.args) == 1:
                self.bad_exit("No Subcommand Instruction Provided perhaps use help", 1)
            else:
                self.bad_exit("Subcommand Not Provided", 1)

    def bad_exit(self, message, status=0):
        # type: (str, int) -> None
        """bad_exit is for when the router needs to bail out"""
        self._grease.message().error(message + '::' + str(list(self.args)))
        print str(message)
        sys.exit(int(status))
