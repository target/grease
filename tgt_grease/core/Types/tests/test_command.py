from unittest import TestCase
from tgt_grease.core.Types import Command
from tgt_grease.core import GreaseContainer


class TestCmd(Command):
    def __init__(self):
        super(TestCmd, self).__init__()

    def execute(self, context):
        return True


class TestCommand(TestCase):
    def test_ioc(self):
        cmd = TestCmd()
        self.assertTrue(isinstance(cmd.ioc, GreaseContainer))
