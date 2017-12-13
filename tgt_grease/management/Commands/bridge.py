from tgt_grease.core.Types import Command


class Bridge(Command):
    """CLI tool for cluster administration"""

    __author__ = "James E. Bell Jr."
    __version__ = "2.0.0"
    purpose = "Control node/cluster operations"
    help = """
    CLI for administrators to manage GREASE Clusters
    
    Args:
        --loop:<int>
            How many scans you would like to perform of cluster
        --foreground
            If set will print log messages to the commandline
    
    """

    def __init__(self):
        super(Bridge, self).__init__()

    def execute(self, context):
        """This method monitors the environment

        An [in]finite loop monitoring the cluster nodes for unhealthy ones

        Args:
            context (dict): context for the command to use

        Returns:
            bool: Command Success

        """
        if context.get('register'):
            print("Working on it!")
        else:
            print("Sub-command Not Found! Here is the help information:")
            print(self.help)
            return False
        return True
