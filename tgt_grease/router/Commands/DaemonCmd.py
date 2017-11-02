from tgt_grease.core.Types import Command


class Daemon(Command):
    """Daemon Class for the daemon"""

    __author__ = "James E. Bell Jr."
    __version__ = "2.0.0"
    purpose = "Control Daemon Processing in GREASE"
    help = """
    Provide simple abstraction for daemon operations in GREASE
    
    Args:
        install
            install the daemon on the system 
        start
            start the daemon
        stop
            stop the daemon
        run
            run the daemon in the foreground    
    
    """

    def __init__(self):
        super(Daemon, self).__init__()

    def execute(self, context):
        return True
