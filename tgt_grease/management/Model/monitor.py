from tgt_grease.core import GreaseContainer


class NodeMonitoring(object):
    """Monitors cluster nodes for unhealthy state

    Attributes:
        ioc (GreaseContainer): IoC Access

    """

    def __init__(self, ioc=None):
        if isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()

    def monitor(self):
        """Monitoring process

        Returns:
            bool: If successful monitoring run occurred

        """
        return True
