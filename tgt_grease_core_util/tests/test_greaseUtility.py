from unittest import TestCase
from tgt_grease_core_util import GreaseUtility
from tgt_grease_core_util import Logging

class test_greaseUtility(TestCase):
    def test_message(self):
        inst = GreaseUtility.Grease()
        self.assertEqual(type(inst.message()), type(Logging.Logger()))
