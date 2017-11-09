from tgt_grease.core import GreaseContainer


class Deduplication(object):
    """Responsible for Deduplication Operations

    Attributes:
        ioc (GreaseContainer): IoC access for DeDuplication

    """

    def __init__(self, ioc):
        if isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()

    def Deduplicate(self, data, collection):
        """Deduplicate data

        This method will deduplicate the `data` object to allow for only unique objects to be returned. The collection
        variable will be the collection deduplication data will be stored in

        Args:
            data (list[dict]): **list or single dimensional dictionaries** to deduplicate
            collection (str): Deduplication collection to use

        Returns:
            list[dict]: Deduplicated data

        """
        # TODO: Deduplicate
        return data
