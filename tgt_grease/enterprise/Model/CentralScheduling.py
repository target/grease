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

    def scheduleSource(self, source, data):
        """Schedule a Source Parse to detection

        This method will take a list of single dimension dictionaries and schedule them for detection

        Args:
            source (str): Name of the source
            data (list[dict]): Data to be scheduled for detection

        Returns:
            bool: Scheduling success

        """
        if len(data) is 0 or not isinstance(data, dict):
            self.ioc.getLogger().trace("", trace=True)
            return False
        self.ioc.getLogger().trace("Preparing to schedule [{0}] source objects".format(len(data)), trace=True)
        sourceCollect = self.ioc.getCollection('SourceData')
        # begin scheduling loop of each block
        for elem in data:
            continue
        return True

    def determineDetectionServer(self):
        """Determines detection server to use

        Finds the detection server available for a new detection job

        Returns:
            str: MongoDB Object ID of server; if one cannot be found then string will be empty

        """
        result = self.ioc.getCollection('JobServer').find({
            'prototypes': 'detect'
        }).limit(1)
