from unittest import TestCase
import os
from tgt_grease_core_util import Logging
from logging import Logger


class test_logging(TestCase):
    def test_is_object_LogFile(self):
        log = Logging.Logger()
        self.assertTrue(log.get_logger(), Logger)
        del log

    def test_log_get_messages(self):
        log = Logging.Logger()
        log.debug('random message')
        self.assertEqual(1, len(log.get_messages()))
        del log

    def test_empty_logger(self):
        log = Logging.Logger()
        log.debug('random message')
        log.get_messages_dump()
        self.assertEqual(0, len(log.get_messages()))
        del log

    def test_log_file_write_line(self):
        log = Logging.Logger()
        if os.name == 'nt':
            self._win_test(log)
        else:
            self._nux_test(log)
        del log

    def _win_test(self, logger):
        # test for directory
        self.assertTrue(os.path.isdir('C:\\grease'))
        # test log file exists
        self.assertTrue(os.path.isfile('C:\\grease\\grease.log'))
        # test line count
        original = sum(1 for line in open('C:\\grease\\grease.log'))
        logger.debug("I'm a test message")
        final = sum(1 for line in open('C:\\grease\\grease.log'))
        self.assertEqual(original + 1, final)

    def _nux_test(self, logger):
        # test for directory
        self.assertTrue(os.path.isdir('/tmp/grease'))
        # test log file exists
        self.assertTrue(os.path.isfile('/tmp/grease/grease.log'))
        # test line count
        original = sum(1 for line in open('/tmp/grease/grease.log'))
        logger.debug("I'm a test message")
        final = sum(1 for line in open('/tmp/grease/grease.log'))
        self.assertEqual(original + 1, final)
