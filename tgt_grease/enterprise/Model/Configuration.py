from tgt_grease.core import GreaseContainer


class PrototypeConfig(object):
    """Responsible for Scanning/Detection/Scheduling configuration

    Attributes:
        ioc (GreaseContainer): IOC access

    """

    def __init__(self, ioc=None):
        if ioc and isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()
