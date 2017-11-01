from unittest import TestCase
from tgt_grease.core.Types import Command
from tgt_grease.core import GreaseContainer


class TestCmd(Command):
    def __init__(self):
        super(TestCmd, self).__init__()

    def execute(self, context):
        for key, val in context.iteritems():
            self.setRetData(key, val)
        return True


class TestCommand(TestCase):
    def test_ioc(self):
        cmd = TestCmd()
        self.assertTrue(isinstance(cmd.ioc, GreaseContainer))

    def test_variable_storage(self):
        cmd = TestCmd()
        self.assertEqual(cmd.variable_storage.name, "TestCmd")

    def test_get_exec_info(self):
        cmd = TestCmd()
        cmd.safe_execute({})
        self.assertTrue(isinstance(cmd.getExecVal(), bool))

    def test_get_ret_val_info(self):
        cmd = TestCmd()
        cmd.safe_execute({})
        self.assertTrue(isinstance(cmd.getRetVal(), bool))

    def test_get_ret_data(self):
        cmd = TestCmd()
        cmd.safe_execute({'key': 'value'})
        self.assertDictEqual(cmd.getRetData(), {'key': 'value'})
