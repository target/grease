from tgt_grease.core import GreaseContainer
from tgt_grease.core import ImportTool


class Detection(object):
    """Detection class for GREASE detect

    This is the model to actually utilize the detectors to parse the sources from scan

    Attributes:
        ioc (GreaseContainer): IOC for scanning
        impTool (ImportTool): Import Utility Instance

    """

    def __init__(self, ioc=None):
        if ioc and isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()
        self.impTool = ImportTool(ioc.getLogger())

    def detectSource(self):
        """This will perform detection the oldest source from SourceData"""
