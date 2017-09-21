from unittest import TestCase
from tgt_grease_core import GreaseRouter
from tgt_grease_core import GreaseCommand


class test_command(GreaseCommand):
    def execute(self):
        return True


class TestRouter(TestCase):
    """class TestRouter tests router logic"""
    def test_is_router(self):
        """test_is_router tests type returned from newing up"""
        router = GreaseRouter.Router()
        self.assertTrue(router, GreaseRouter.Router)
