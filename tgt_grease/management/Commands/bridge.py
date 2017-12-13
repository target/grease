from tgt_grease.core.Types import Command


class Bridge(Command):
    """CLI tool for cluster administration"""

    __author__ = "James E. Bell Jr."
    __version__ = "2.0.0"
    purpose = "Control node/cluster operations"
    help = """
    CLI for administrators to manage GREASE Clusters
    
    Args:
        register
            register this node with a GREASE Cluster as provided in the configuration file
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
        retVal = False
        if context.get('foreground'):
            self.ioc.getLogger().foreground = True
        if 'register' in context.get('grease_other_args', []):
            self.ioc.getLogger().debug("Registration Requested")
            if self.ioc.ensureRegistration():
                print("Registration Complete!")
                self.ioc.getLogger().info("Registration Completed Successfully")
                retVal = True
            else:
                print("Registration Failed!")
                self.ioc.getLogger().info("Registration Failed")
        else:
            print("Sub-command Not Found! Here is the help information:")
            print(self.help)
            retVal = False
        if context.get('foreground'):
            self.ioc.getLogger().foreground = False
        return retVal
