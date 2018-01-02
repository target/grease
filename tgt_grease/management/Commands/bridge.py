from tgt_grease.core.Types import Command
from tgt_grease.management.Model import BridgeCommand


class Bridge(Command):
    """CLI tool for cluster administration

    The command palate is listed here::

        Args:
            register
                register this node with a GREASE Cluster as provided in the configuration file
            info
                --node:<ObjectID>
                    !Optional! parameter to observe a remote node. Defaults to look at self
                --jobs
                    !Optional! if set will list jobs executed
                --pJobs
                    !Optional! include Prototype Jobs in list of jobs
            assign
                --prototype:<string>
                    !mandatory if assigning a prototype! prototype to assign
                    !NOTE! THIS MUST BE SEPARATED BY COLON OR EQUAL SIGN
                --role:<string>
                    !mandatory if assigning a role! role to assign
                    !NOTE! THIS MUST BE SEPARATED BY COLON OR EQUAL SIGN
                --node:<ObjectID>
                    !Optional! remote node to assign job to
            unassign
                --prototype:<string>
                    !mandatory if unassigning a prototype! prototype to unassign
                    !NOTE! THIS MUST BE SEPARATED BY COLON OR EQUAL SIGN
                --role:<string>
                    !mandatory if unassigning a role! role to unassign
                    !NOTE! THIS MUST BE SEPARATED BY COLON OR EQUAL SIGN
                --node:<ObjectID>
                    !Optional! remote node to unassign job to
            cull
                --node:<ObjectID>
                    !Optional! parameter to cull a remote node. Defaults to look at self
            activate
                --node:<ObjectID>
                    !Optional! parameter to activate a remote node. Defaults to look at self
            --foreground
                If set will print log messages to the commandline

    Note:
        This tool is ever evolving! If you need something more feel free to create an issue!

    Attributes:
        bridge (BridgeCommand): Model Instance

    """

    __author__ = "James E. Bell Jr."
    __version__ = "2.0.0"
    purpose = "Control node/cluster operations"
    help = """
    CLI for administrators to manage GREASE Clusters
    
    Args:
        register
            register this node with a GREASE Cluster as provided in the configuration file
        info
            --node:<ObjectID>
                !Optional! parameter to observe a remote node. Defaults to look at self
            --jobs
                !Optional! if set will list jobs executed
            --pJobs
                !Optional! include Prototype Jobs in list of jobs
        assign
            --prototype:<string>
                !mandatory if assigning a prototype! prototype to assign
                !NOTE! THIS MUST BE SEPARATED BY COLON OR EQUAL SIGN
            --role:<string>
                !mandatory if assigning a role! role to assign
                !NOTE! THIS MUST BE SEPARATED BY COLON OR EQUAL SIGN
            --node:<ObjectID>
                !Optional! remote node to assign job to
        unassign
            --prototype:<string>
                !mandatory if unassigning a prototype! prototype to unassign
                !NOTE! THIS MUST BE SEPARATED BY COLON OR EQUAL SIGN
            --role:<string>
                !mandatory if unassigning a role! role to unassign
                !NOTE! THIS MUST BE SEPARATED BY COLON OR EQUAL SIGN
            --node:<ObjectID>
                !Optional! remote node to unassign job to
        cull
            --node:<ObjectID>
                !Optional! parameter to cull a remote node. Defaults to look at self
        activate
            --node:<ObjectID>
                !Optional! parameter to activate a remote node. Defaults to look at self
        --foreground
            If set will print log messages to the commandline
    
    """

    def __init__(self):
        super(Bridge, self).__init__()
        self.bridge = BridgeCommand(self.ioc)

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
            retVal = self.bridge.action_register()
        elif 'info' in context.get('grease_other_args', []):
            retVal = self.bridge.action_info(context.get('node'), context.get('jobs'), context.get('pJobs'))
        elif 'assign' in context.get('grease_other_args', []):
            retVal = self.bridge.action_assign(context.get('prototype'), context.get('role'), context.get('node'))
        elif 'unassign' in context.get('grease_other_args', []):
            retVal = self.bridge.action_unassign(context.get('prototype'), context.get('role'), context.get('node'))
        elif 'cull' in context.get('grease_other_args', []):
            retVal = self.bridge.action_cull(context.get('node'))
        elif 'activate' in context.get('grease_other_args', []):
            retVal = self.bridge.action_activate(context.get('node'))
        else:
            print("Sub-command Not Found! Here is the help information:")
            print(self.help)
            retVal = False
        if context.get('foreground'):
            self.ioc.getLogger().foreground = False
        return retVal
