import os
import time
import logging
from collections import deque
from logging.config import fileConfig
from .Notifier import Notifier
from .Configuration import Configuration
from datetime import datetime
# POSTGRES
from sqlalchemy.exc import OperationalError


GREASE_LOG_HANDLER = None


class Logger:
    _config = Configuration()
    _unregisteredMode = False
    _current_minute = datetime.utcnow().minute

    def __init__(self):
        global GREASE_LOG_HANDLER
        self.start_time = time.time()
        self._messages = deque(())
        self._notifier = Notifier()
        if os.path.isfile(self._config.identity_file):
            try:
                self._node_id = self._config.node_db_id()
            except OperationalError:
                self._node_id = self._config.identity
        else:
            self._node_id = "UNREGISTERED"
        # Setup Log Configuration
        if type(self._config.get('GREASE_LOG_FILE')) == str and os.path.isfile(self._config.get('GREASE_LOG_FILE')):
            fileConfig(self._config.get('GREASE_LOG_FILE'))
            self._logger = logging.getLogger('GREASE')
        else:
            logFilename = self._config.grease_dir + self._config.fs_Separator + "grease.log"
            self._logger = logging.getLogger('GREASE')
            self._logger.setLevel(logging.DEBUG)
            self._formatter = logging.Formatter(
                "{\"timestamp\": \"%(asctime)s.%(msecs)03d\", \"node\": \""
                + str(self._node_id)
                + "\", \"thread\": \"%(threadName)s\", \"level\" : \"%(levelname)s\", \"message\" : \"%(message)s\"}",
                "%Y-%m-%d %H:%M:%S"
            )
            self._formatter.converter = time.gmtime
            if not GREASE_LOG_HANDLER:
                GREASE_LOG_HANDLER = logging.FileHandler(logFilename)
                GREASE_LOG_HANDLER.setLevel(logging.DEBUG)
                GREASE_LOG_HANDLER.setFormatter(self._formatter)
                self._logger.addHandler(GREASE_LOG_HANDLER)

    def __del__(self):
        return

    def get_logger(self):
        # type: () -> logging
        return self._logger

    def get_messages(self):
        # type: () -> deque
        return self._messages

    def get_messages_dump(self):
        # type: () -> deque
        messages = self._messages
        self._messages = deque(())
        return messages

    def dress_message(self, message, level, hipchat, verbose, message_color='gray'):
        # type: (str, str, bool, bool, str) -> str
        if self._current_minute != datetime.utcnow().minute:
            self._messages = deque(())
            self._current_minute = datetime.utcnow().minute
        message = "[{0}]::".format(str(self._node_id)) + message
        if verbose:
            message = "VERBOSE::" + message
        message = "{0}::".format(level) + message
        if hipchat:
            self._notifier.send_hipchat_message(message, message_color)
        return message

    def debug(self, message, verbose=False, hipchat=False):
        # type: (str, bool, bool) -> bool
        message = self.dress_message(message, "DEBUG", hipchat, verbose, 'gray')
        if verbose:
            if not self._config.get('GREASE_VERBOSE_LOGGING'):
                return True
        self._messages.append(('DEBUG', time.time(), message))
        return self._logger.debug(message)

    def info(self, message, verbose=False, hipchat=False):
        # type: (str, bool, bool) -> bool
        message = self.dress_message(message, "INFO", hipchat, verbose, 'purple')
        if verbose:
            if not self._config.get('GREASE_VERBOSE_LOGGING'):
                return True
        self._messages.append(('INFO', time.time(), message))
        return self._logger.info(message)

    def warning(self, message, verbose=False, hipchat=False):
        # type: (str, bool, bool) -> bool
        message = self.dress_message(message, "WARNING", hipchat, verbose, 'yellow')
        if verbose:
            if not self._config.get('GREASE_VERBOSE_LOGGING'):
                return True
        self._messages.append(('WARNING', time.time(), message))
        return self._logger.warning(message)

    def error(self, message, verbose=False, hipchat=False):
        # type: (str, bool, bool) -> bool
        message = self.dress_message(message, "ERROR", hipchat, verbose, 'red')
        if verbose:
            if not self._config.get('GREASE_VERBOSE_LOGGING'):
                return True
        self._messages.append(('ERROR', time.time(), message))
        return self._logger.error(message)

    def critical(self, message):
        # type: (str) -> bool
        message = self.dress_message(message, "CRITICAL", True, False, 'red')
        self._messages.append(('CRITICAL', time.time(), message))
        return self._logger.critical(message)

    def exception(self, message):
        # type: (str) -> bool
        message = self.dress_message(message, "EXCEPTION", True, False, 'red')
        self._messages.append(('EXCEPTION', time.time(), message))
        return self._logger.exception(message)
