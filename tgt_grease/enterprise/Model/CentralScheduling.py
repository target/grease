from tgt_grease.core import GreaseContainer


class Scheduling(object):
    """Central scheduling class for GREASE

    This class routes data to nodes within GREASE

    Attributes:
        ioc (GreaseContainer): IoC access for DeDuplication

    """

    def __init__(self, ioc):
        if isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()

    def ScheduleSource(self, data):
        """Schedule a Source Parse to detection

        This method will take a list of single dimension dictionaries and schedule them for detection

        Args:
             data (list[dict]): Data to be scheduled for detection

        Returns:
            bool: Scheduling success

        """
        # TODO: All of this
        return True
