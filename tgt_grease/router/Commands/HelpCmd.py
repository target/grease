from tgt_grease.core.Types import Command
from tgt_grease.core import ImportTool
import importlib


class Help(Command):
    """The Help Command for GREASE

    Meant to provide a rich CLI Experience to users to enable quick help

    """

    purpose = "Provide Help Information"
    help = """
    Provide help information to users of GREASE about available commands. This though
    is just a demo of what you could print. Really it could be anything I suppose!
    
    Args:
        None
    """
    __author__ = "James E. Bell Jr."
    __version__ = "1.0.0"

    def __init__(self):
        super(Help, self).__init__()

    def execute(self, context):
        print("")
        print("Welcome to GREASE Help")
        impTool = ImportTool(self.ioc.getLogger())
        for route in self.ioc.getConfig().get('Import', 'searchPath'):
            mod = importlib.import_module(route)
            for attr in dir(mod):
                cmd = impTool.load(attr)
                if cmd and isinstance(cmd, Command):
                    print("<======================>")
                    print("[{0}] Purpose: [{1}]".format(
                        cmd.__class__.__name__,
                        cmd.purpose
                    ))
                    print("Author: {0}".format(cmd.__author__))
                    print("Current Version: {0}".format(cmd.__version__))
                    if cmd.os_needed:
                        print('Needs OS: {0}'.format(cmd.os_needed))
                    print(cmd.help)
                    print("<======================>")
        return True
