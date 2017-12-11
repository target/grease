from tgt_grease.core.Types import Command
from tgt_grease.management.Model import NodeMonitoring


class ClusterMonitor(Command):
    """Cluster Monitor to ensure nodes are alive"""

    __author__ = "James E. Bell Jr."
    __version__ = "2.0.0"
    purpose = "Control cluster health"
    help = """
    Ensures health of GREASE cluster by providing a Prototype to
    scan the active nodes and disable those that are unhealthy
    
    Args:
        --loop:<int>
            How many scans you would like to perform of cluster
    
    """

    def __init__(self):
        super(ClusterMonitor, self).__init__()

    def execute(self, context):
        """This method monitors the environment

        An [in]finite loop monitoring the cluster nodes for unhealthy ones

        Args:
            context (dict): context for the command to use

        Returns:
            bool: Command Success

        """
        mgr = NodeMonitoring(self.ioc)
        if context.get('loop'):
            runs = 0
            while runs < int(context.get('loop', 0)):
                if not mgr.monitor():
                    self.ioc.getLogger().error("Monitoring Process Failed", notify=False)
        else:
            while True:
                if not mgr.monitor():
                    self.ioc.getLogger().error("Monitoring Process Failed", notify=False)
        return True
