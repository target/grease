from tgt_grease.core.Types import Command
from tgt_grease.management.Model import NodeMonitoring
import random
import time


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
        --foreground
            If set will print log messages to the commandline
    
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
        if context.get('foreground'):
            self.ioc.getLogger().foreground = True
        monitor = NodeMonitoring(self.ioc)
        if context.get('loop'):
            i = 0
            while i < int(context.get('loop', 0)):
                if not monitor.monitor():
                    self.ioc.getLogger().error("Monitoring Process Failed", notify=False)
                else:
                    monitor.scanComplete()
                i += 1
                time.sleep(5)
        else:
            while True:
                if not monitor.monitor():
                    self.ioc.getLogger().error("Monitoring Process Failed", notify=False)
                else:
                    monitor.scanComplete()
                # sleep for a random interval to ensure not all nodes poll at the same time
                time.sleep(int(str(random.choice(range(1, 5))) + str(random.choice(range(0, 9)))))
        if context.get('foreground'):
            self.ioc.getLogger().foreground = False
        return True
