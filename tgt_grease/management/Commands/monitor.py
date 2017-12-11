from tgt_grease.core.Types import Command


class ClusterMonitor(Command):
    """Cluster Monitor to ensure nodes are alive"""

    __author__ = "James E. Bell Jr."
    __version__ = "2.0.0"
    purpose = "Control cluster health"
    help = """
    Ensures health of GREASE cluster
    
    """

    def __init__(self):
        super(ClusterMonitor, self).__init__()

    def execute(self, context):
        """"""
        print(context)
        return True
