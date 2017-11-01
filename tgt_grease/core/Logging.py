from tgt_grease.core import Configuration
from logging import config
import logging
import os
import time

GREASE_LOG_HANDLER = None


class Logging(object):
    """Application Logging for GREASE

    This is the primary configuration source for GREASE logging. All log information will be passed here to
    enable centralized log aggregation

    Attributes:
        conf (Configuration): This is an instance of the Config to enable configuring loggers
        _logger (logging.Logger): This is the actual logger for GREASE
        _formatter (logging.Formatter): This is the log formatter

    """

    conf = None
    _logger = None
    _formatter = None

    def __init__(self, Config=None):
        if isinstance(Config, Configuration):
            self.conf = Config
        else:
            self.conf = Configuration()
        self.ProvisionLoggers()

    def getConfig(self):
        """Getter for Configuration

        Returns:
            Configuration: The loaded configuration object

        """
        return self.conf

    def TriageMessage(self, message, additional=None, verbose=False, trace=False, notify=False, level=logging.DEBUG):
        """Central message handler

        Args:
            message (str): Message to Log
            additional (object): Additional information to log
            verbose (bool): To be printed if verbose is enabled
            trace (bool): To be printed if trace is enabled
            notify (bool): If true will pass through notification system
            level (int): Log Level

        Returns:
            bool: Log Success

        """
        # first prevent verbose processing
        if verbose and not self.conf.get('Logging', 'verbose'):
            return True
        # prevent trace processing
        if trace and not self.conf.get('Logging', 'trace'):
            return True
        # create a pre-message
        if level is 0:
            preMsg = "TRACE"
        elif level is logging.DEBUG:
            preMsg = "DEBUG"
        elif level is logging.INFO:
            preMsg = "INFO"
        elif level is logging.WARNING:
            preMsg = "WARNING"
        elif level is logging.ERROR:
            preMsg = "ERROR"
        elif level is logging.CRITICAL:
            preMsg = "CRITICAL"
        else:
            preMsg = "UNSET"
        if verbose:
            preMsg = "VERBOSE::{0}".format(preMsg)
        if trace:
            preMsg = "TRACE::{0}".format(preMsg)
        message = "{0}::{1}::{2}::{3}".format(preMsg, self.conf.NodeIdentity, message, additional)
        # Foreground mode print log messages
        if self.conf.get('Logging', 'foreground'):
            print(message)
        # actually log the message
        if level is 0:
            self._logger.log(logging.DEBUG, message)
        else:
            self._logger.log(level, message)
        # notify if needed
        if notify:
            # TODO: Third Party Notifications
            return True
        return True

    def trace(self, message, additional=None, verbose=False, trace=False, notify=False):
        """Trace Messages

        Use this method for logging tracing (enhanced debug) statements

        Args:
            message (str): Message to log
            additional (object): Additional information to log. Note: object must be able to transform to string
            verbose (bool): Print only if verbose mode
            trace (bool): Print only if trace mode
            notify (bool): Run through the notification management system

        Returns:
            bool: Message is logged

        """
        return bool(self.TriageMessage(
            message,
            additional=additional,
            verbose=verbose,
            trace=trace,
            notify=notify,
            level=0
        ))

    def debug(self, message, additional=None, verbose=False, trace=False, notify=False):
        """Debug Messages

        Use this method for logging debug statements

        Args:
            message (str): Message to log
            additional (object): Additional information to log. Note: object must be able to transform to string
            verbose (bool): Print only if verbose mode
            trace (bool): Print only if trace mode
            notify (bool): Run through the notification management system

        Returns:
            bool: Message is logged

        """
        return bool(self.TriageMessage(
            message,
            additional=additional,
            verbose=verbose,
            trace=trace,
            notify=notify,
            level=logging.DEBUG
        ))

    def info(self, message, additional=None, verbose=False, trace=False, notify=False):
        """Info Messages

        Use this method for logging info statements

        Args:
            message (str): Message to log
            additional (object): Additional information to log. Note: object must be able to transform to string
            verbose (bool): Print only if verbose mode
            trace (bool): Print only if trace mode
            notify (bool): Run through the notification management system

        Returns:
            bool: Message is logged

        """
        return bool(self.TriageMessage(
            message,
            additional=additional,
            verbose=verbose,
            trace=trace,
            notify=notify,
            level=logging.INFO
        ))

    def warning(self, message, additional=None, verbose=False, trace=False, notify=False):
        """Warning Messages

        Use this method for logging warning statements

        Args:
            message (str): Message to log
            additional (object): Additional information to log. Note: object must be able to transform to string
            verbose (bool): Print only if verbose mode
            trace (bool): Print only if trace mode
            notify (bool): Run through the notification management system

        Returns:
            bool: Message is logged

        """
        return bool(self.TriageMessage(
            message,
            additional=additional,
            verbose=verbose,
            trace=trace,
            notify=notify,
            level=logging.WARNING
        ))

    def error(self, message, additional=None, verbose=False, trace=False, notify=False):
        """Error Messages

        Use this method for logging error statements

        Args:
            message (str): Message to log
            additional (object): Additional information to log. Note: object must be able to transform to string
            verbose (bool): Print only if verbose mode
            trace (bool): Print only if trace mode
            notify (bool): Run through the notification management system

        Returns:
            bool: Message is logged

        """
        return bool(self.TriageMessage(
            message,
            additional=additional,
            verbose=verbose,
            trace=trace,
            notify=notify,
            level=logging.ERROR
        ))

    def critical(self, message, additional=None, verbose=False, trace=False, notify=False):
        """Critical Messages

        Use this method for logging critical statements

        Args:
            message (str): Message to log
            additional (object): Additional information to log. Note: object must be able to transform to string
            verbose (bool): Print only if verbose mode
            trace (bool): Print only if trace mode
            notify (bool): Run through the notification management system

        Returns:
            bool: Message is logged

        """
        return bool(self.TriageMessage(
            message,
            additional=additional,
            verbose=verbose,
            trace=trace,
            notify=notify,
            level=logging.CRITICAL
        ))

    def ProvisionLoggers(self):
        """Loads Log Handler & Config

        Returns:
            None: Simple loader, Nothing needed

        """
        if self.conf.get('Logging', 'ConfigurationFile'):
            if os.path.isfile(self.conf.get('Logging', 'ConfigurationFile')):
                config.fileConfig(self.conf.get('Logging', 'ConfigurationFile'))
                self._logger = logging.getLogger('GREASE')
            else:
                self.DefaultLogger()
        else:
            self.DefaultLogger()

    def DefaultLogger(self):
        """Default Logging Provisioning

        Returns:
            None: void method to provision class internals

        """
        global GREASE_LOG_HANDLER
        logFilename = self.conf.get('Logging', 'file')
        self._logger = logging.getLogger('GREASE')
        self._logger.setLevel(logging.DEBUG)
        self._formatter = logging.Formatter(
            "{"
            "\"timestamp\": \"%(asctime)s.%(msecs)03d\", "
            "\"thread\": \"%(threadName)s\", "
            "\"level\" : \"%(levelname)s\", "
            "\"message\" : \"%(message)s\"}",
            "%Y-%m-%d %H:%M:%S"
        )
        self._formatter.converter = time.gmtime
        if not GREASE_LOG_HANDLER:
            GREASE_LOG_HANDLER = logging.FileHandler(logFilename)
            GREASE_LOG_HANDLER.setLevel(logging.DEBUG)
            GREASE_LOG_HANDLER.setFormatter(self._formatter)
            self._logger.addHandler(GREASE_LOG_HANDLER)
