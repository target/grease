from abc import ABCMeta, abstractmethod


class BaseSourceClass(object):
    """Base Class for all sources to implement

    Attributes:
        _data (list[dict]): List of data to be returned to GREASE
        deduplication_strength (float): Level of deduplication strength to use *higher is stronger uniqueness*
        field_set (None or list): If none all fields found will be duplicated otherwise only fields listed will be
        deduplication_expiry (int): Hours to retain deduplication data
        deduplication_expiry_max (int): Days to deduplicate for **maximum**

    """

    __metaclass__ = ABCMeta

    def __init__(self):
        self._data = []
        self.deduplication_strength = 85.0
        self.deduplication_expiry = 12
        self.deduplication_expiry_max = 7
        self.field_set = None

    @abstractmethod
    def mock_data(self, configuration):
        """Mock the source for data

        Use this method to read through configuration provided to you, and mock getting data. This will *always* be
        called by the scan engine. **Ensure you set any data to the `self._data` variable. A list of dictionaries for
        the engine to schedule for detection**

        Args:
            configuration (dict): Configuration for the sourcing to occur with

        Note:
            This is the method to fill out to get data into GREASE.

        Returns:
            list[dict]: mock data from source

        """
        pass

    @abstractmethod
    def parse_source(self, configuration):
        """Parse the source for data

        Use this method to read through configuration provided to you, and get data. This will *always* be called
        by the scan engine. **Ensure you set any data to the `self._data` variable. A list of dictionaries for the
        engine to schedule for detection**

        Args:
            configuration (dict): Configuration for the sourcing to occur with

        Note:
            This is the method to fill out to get data into GREASE.

        Returns:
            bool: If True data will be scheduled for ingestion after deduplication. If False the engine will bail out

        """
        pass

    def get_data(self):
        """Returns data from source

        Returns:
            list[dict]: List of *single dimension* dictionaries for GREASE to parse through other prototypes

        """
        return self._data
