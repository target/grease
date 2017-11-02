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
        if 'install' in context.get('grease_other_args'):
            return bool(self.install())
        elif 'start' in context.get('grease_other_args'):
            return bool(self.start())
        elif 'stop' in context.get('grease_other_args'):
            return bool(self.stop())
        elif 'run' in context.get('grease_other_args'):
            try:
                self.run()
                return True
            except KeyboardInterrupt:
                return True
        else:
            return False

    def install(self):
        """Handle Daemon Installation based on the platform we're working with

        Returns:
            bool: installation success

        """
        pass

    def run(self):
        """Actual running of the daemon

        Returns:
            None: Should never return

        """
        pass

    def start(self):
        """Starting the daemon based on platform

        Returns:
            bool: start success

        """
        pass

    def stop(self):
        """Stopping the daemon based on the platform

        Returns:
            bool: stop success

        """
        pass
