from tgt_grease.core import Logging
from tgt_grease.core.Connectivity import Mongo


class GreaseContainer(object):
    """Inversion of Control Container for objects in GREASE"""

    _logger = None
    _mongo = None

    def __init__(self, Logger=None):
        if Logger and isinstance(Logger, Logging):
            self._logger = Logger
        else:
            self._logger = Logging()
        self._mongo = Mongo(self._logger.getConfig())

    def getLogger(self):
        """Get the logging instance

        Returns:
            Logging: The logging instance

        """
        return self._logger

    def getNotification(self):
        """Get the notifications instance

        Returns:
            tgt_grease.core.Notifications: The notifications instance

        """
        return self._logger.getNotification()

    def getMongo(self):
        """Get the Mongo instance

        Returns:
            Mongo: Mongo Instance Connection

        """
        return self._mongo

    def getConfig(self):
        """Gets the Configuration Instance

        Returns:
            tgt_grease.core.Configuration.Configuration: the configuration instance

        """
        return self._logger.getConfig()
