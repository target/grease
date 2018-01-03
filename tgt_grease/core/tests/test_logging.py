from unittest import TestCase
from tgt_grease.core import Configuration, Logging
import os


class TestLogging(TestCase):
    def test_logging_creation_default(self):
        log = Logging()
        self.assertTrue(isinstance(log, Logging))

    def test_logging_creation_with_conf(self):
        conf = Configuration()
        log = Logging(conf)
        self.assertTrue(isinstance(log, Logging))

    def test_config_getter(self):
        log = Logging()
        self.assertTrue(isinstance(log.getConfig(), Configuration))

    def test_debug(self):
        log = Logging()
        initial = self._log_line_count()
        self.assertTrue(log.debug("Test Debug Message", {'key': 'value'}))
        after = self._log_line_count()
        self.assertTrue(initial + 1 == after)

    def test_info(self):
        log = Logging()
        initial = self._log_line_count()
        self.assertTrue(log.info("Test Info Message", {'key': 'value'}))
        after = self._log_line_count()
        self.assertTrue(initial + 1 == after)

    def test_warning(self):
        log = Logging()
        initial = self._log_line_count()
        self.assertTrue(log.warning("Test Warning Message", {'key': 'value'}))
        after = self._log_line_count()
        self.assertTrue(initial + 1 == after)

    def test_error(self):
        log = Logging()
        initial = self._log_line_count()
        self.assertTrue(log.error("Test Error Message", {'key': 'value'}))
        after = self._log_line_count()
        self.assertTrue(initial + 1 == after)

    def test_critical(self):
        log = Logging()
        initial = self._log_line_count()
        self.assertTrue(log.critical("Test Critical Message", {'key': 'value'}))
        after = self._log_line_count()
        self.assertTrue(initial + 1 == after)

    def _log_line_count(self):
        conf = Configuration()
        if os.path.isfile(conf.get('Logging', 'file')):
            fil = open(conf.get('Logging', 'file'), 'r')
            filContent = fil.read().splitlines()
            fil.close()
            del fil
            ctn = 0
            for line in filContent:
                ctn += 1
            del filContent
            del conf
            return ctn
        else:
            del conf
            return 0
