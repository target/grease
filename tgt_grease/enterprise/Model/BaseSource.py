from abc import ABCMeta, abstractmethod


class BaseSourceClass(object):
    """Base Class for all sources to implement

    Attributes:
        _data (list[dict]): List of data to be returned to GREASE

    """

    __metaclass__ = ABCMeta

    def __init__(self):
        self._data = []

    # TODO: Mocking Method

    @abstractmethod
    def parse_source(self, configuration):
        """Parse the source for data

        Use this method to read through configuration provided to you, and get data. This will *always* be called
        by the scan engine. **Ensure you set any data to the `self._data` variable. A list of dictionaries for the
        engine to schedule for detection**

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
