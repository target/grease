from tgt_grease.core import Logging, Configuration, ImportTool
from tgt_grease.core.Types import Command
import os
import sys
import getopt


class GreaseRouter(object):
    """Main GREASE CLI Router

    This class handles routing CLI requests as well as starting the Daemon on Windows/POSIX systems

    Attributes:
        _config (Configuration): Main Configuration Object
        _logger (Logging): Main Logging Instance
        _importTool (ImportTool): Importer Tool Instance
        _exit_message (str): Exit Message

    """

    _config = Configuration(os.environ.get('GREASE_CONF', None))
    _logger = Logging(_config)
    _importTool = ImportTool(_logger)
    _exit_message = None

    def __init__(self):
        self._logger.trace("Router Startup", trace=True)

    def StartGREASE(self):
        """EntryPoint for CLI scripts for GREASE

        Returns:
            None: Void Method for GREASE

        """
        status = self.run()
        self.exit(status, self._exit_message)

    def run(self):
        """Route commands through GREASE

        Returns:
            int: Exit Code

        """
        # ensure at least a sub-command has been provided
        # TODO: Ensure we are loading the job asked for
        if len(sys.argv) > 1:
            inst = self._importTool.load(sys.argv[1])
            if isinstance(inst, Command):
                # Parse long args to command context
                if inst.execute(self.get_arguments()):
                    return 0
                else:
                    return 3
            else:
                self._exit_message = "Command not found"
                return 2
        else:
            self._logger.error("Sub-command not provided")
            self._exit_message = "Sub-command not provided to GREASE CLI"
            return 1

    def exit(self, code, message=None):
        """Exit program with exit code

        Args:
            code (int): Exit Code
            message (str): Exit message if any

        Returns:
            None: Will exit program

        """
        if message:
            self._logger.info("Message: [{0}]".format(message))
            if code != 0:
                print("ERROR: {0}".format("message"))
            else:
                print(message)
        self._logger.debug("GREASE exit code: [{0}]".format(code), verbose=True)
        sys.exit(code)

    @staticmethod
    def get_arguments():
        """Parse CLI long arguments into dictionaries

        This expects arguments separated by space `--opt val`, colon `--opt:val`, or equal `--opt=val` signs

        Returns:
            dict: key->value pairs of arguments

        """
        i = 0
        context = {}
        while i < len(sys.argv):
            arg = str(sys.argv[i])
            if arg.startswith("--"):
                # Found long opt
                if len(arg.split("=")) > 1:
                    # was equal separated
                    context[arg.split("=")[0].strip("--")] = arg.split("=")[1]
                elif len(arg.split(":")) > 1:
                    # was colon separated
                    context[arg.split(":")[0].strip("--")] = arg.split(":")[1]
                else:
                    # space separated
                    context[arg.strip("--")] = sys.argv[i + 1]
                    i += 1
            i += 1
        return context