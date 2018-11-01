from unittest import TestCase
from mock import MagicMock, patch
from tgt_grease.core.Decorators import grease_log


class TestGreaseLogDecorator(TestCase):

    @patch("tgt_grease.core.GreaseContainer.info")
    def test_grease_log_good(self, mock_info):
        mock_info = MagicMock(return_value="Yay. I logged things.")
        self.helper()
        mock_info.assert_called()

    @grease_log
    def helper(self):
        return True


