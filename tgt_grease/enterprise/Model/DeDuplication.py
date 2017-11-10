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

    def Deduplicate(self, data, source, strength, collection, field_set=None):
        """Deduplicate data

        This method will deduplicate the `data` object to allow for only unique objects to be returned. The collection
        variable will be the collection deduplication data will be stored in

        Args:
            data (list[dict]): **list or single dimensional dictionaries** to deduplicate
            source (str): Source of data being deduplicated
            strength (float): Strength of deduplication (higher is more unique)
            collection (str): Deduplication collection to use
            field_set (list, optional): Fields to deduplicate on

        Returns:
            list[dict]: Deduplicated data

        """
        # ensure we got a list
        if not isinstance(data, list):
            self.ioc.getLogger().error(
                "Data was not of type list for Deduplication got type [{0}]".format(str(type(data))),
                notify=False,
                verbose=True
            )
            return []
        # ensure there is data to parse
        if len(data) <= 0:
            # empty list return empty lists
            return []

        return data
