from unittest import TestCase
from mock import patch
from tgt_grease.core.Decorators import grease_log


class TestGreaseLogDecorator(TestCase):

    @patch("tgt_grease.core.Logging.info")
    def test_grease_log_noarg(self, mock_info):
        @grease_log
        def noarg_helper():
            return True

        mock_info.return_value = "Yay. I logged things."
        noarg_helper()
        mock_info.assert_called()

    @patch("tgt_grease.core.Logging.critical")
    def test_grease_log_critical(self, mock_critical):
        @grease_log(level="critical")
        def critical_helper():
            return True

        mock_critical.return_value = "Yay. I logged things."
        critical_helper()
        mock_critical.assert_called()

    @patch("tgt_grease.core.Logging.warning")
    def test_grease_log_warning(self, mock_warning):
        @grease_log(level="warning")
        def warning_helper():
            return True

        mock_warning.return_value = "Yay. I logged things."
        warning_helper()
        mock_warning.assert_called()

    @patch("tgt_grease.core.Logging.debug")
    def test_grease_log_debug(self, mock_debug):
        @grease_log(level="debug")
        def debug_helper():
            return True

        mock_debug.return_value = "Yay. I logged things."
        debug_helper()
        mock_debug.assert_called()

    @patch("tgt_grease.core.Logging.trace")
    def test_grease_log_trace(self, mock_trace):
        @grease_log(level="trace")
        def trace_helper():
            return True

        mock_trace.return_value = "Yay. I logged things."
        trace_helper()
        mock_trace.assert_called()



