from unittest import TestCase
from tgt_grease_core_util import Configuration
from tgt_grease_core_util import Logging
from logging import Logger


class test_logging(TestCase):

    _config = Configuration()

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
        # test for directory
        self.assertTrue(self._config.grease_dir + self._config.fs_Separator)
        # test log file exists
        self.assertTrue(self._config.grease_dir + self._config.fs_Separator + "grease.log")
        # test line count
        original = sum(1 for line in open(self._config.grease_dir + self._config.fs_Separator + "grease.log"))
        log.debug("I'm a test message")
        final = sum(1 for line in open(self._config.grease_dir + self._config.fs_Separator + "grease.log"))
        self.assertEqual(original + 1, final)
