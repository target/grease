from os import name as op_name
from os import path
from os import getenv
from os import mkdir
import time
import logging
from collections import deque
from logging.config import fileConfig
import random
from Notifier import Notifier


class Logger:

    def __init__(self):
        self.start_time = time.time()
        self._messages = deque(())
        self._notifier = Notifier()
        # Setup Log Configuration
        if type(getenv('GREASE_LOG_FILE')) == str and path.isfile(getenv('GREASE_LOG_FILE')):
            fileConfig(getenv('GREASE_LOG_FILE'))
            self._logger = logging.getLogger('GREASE-' + str(random.random()))
        else:
            if op_name == 'nt':
                logDir = "C:\\grease"
            else:
                logDir = "/tmp/grease"
            if not path.isdir(logDir):
                mkdir(logDir)
            logFilename = path.join(logDir, "grease.log") 
            self._logger = logging.getLogger('GREASE-' + str(random.random()))
            self._logger.setLevel(logging.DEBUG)
            self._handler = logging.FileHandler(logFilename)
            self._handler.setLevel(logging.DEBUG)
            self._formatter = logging.Formatter("{\"timestamp\": \"%(asctime)s.%(msecs)03d\", \"level\" : \"%(levelname)s\", \"message\" : \"%(message)s\"}", "%Y-%m-%d %H:%M:%S")
            self._handler.setFormatter(self._formatter)
            self._logger.addHandler(self._handler)

    def __del__(self):
        self._logger.removeHandler(self._handler)

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

    def debug(self, message, verbose=False):
        # type: (str, bool) -> bool
        if verbose:
            if not getenv('GREASE_VERBOSE_LOGGING'):
                return True
            else:
                message = "VERBOSE::" + str(message).encode('utf-8')
        message = str(message).encode('utf-8')
        self._messages.append(('DEBUG', time.time(), message))
        return self._logger.debug(message)

    def info(self, message):
        # type: (str) -> bool
        message = str(message).encode('utf-8')
        self._messages.append(('INFO', time.time(), message))
        return self._logger.info(message)

    def warning(self, message):
        # type: (str) -> bool
        message = str(message).encode('utf-8')
        self._messages.append(('WARNING', time.time(), message))
        return self._logger.warning(message)

    def error(self, message):
        # type: (str) -> bool
        message = str(message).encode('utf-8')
        self._messages.append(('ERROR', time.time(), message))
        return self._logger.error(message)

    def critical(self, message):
        # type: (str) -> bool
        message = str(message).encode('utf-8')
        self._messages.append(('CRITICAL', time.time(), message))
        self._notifier.send_hipchat_message(message)
        return self._logger.critical(message)

    def exception(self, message):
        # type: (str) -> bool
        message = str(message).encode('utf-8')
        self._messages.append(('EXCEPTION', time.time(), message))
        self._notifier.send_hipchat_message(message)
        return self._logger.exception(message)
