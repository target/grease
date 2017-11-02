from unittest import TestCase
from tgt_grease.core.Types import Command
from tgt_grease.core import GreaseContainer


class TestCmd(Command):
    def __init__(self):
        super(TestCmd, self).__init__()

    def execute(self, context):
        for key, val in context.items():
            self.setData(key, val)
        return True


class TestCmdFail(Command):
    def __init__(self):
        super(TestCmdFail, self).__init__()

    def execute(self, context):
        for key, val in context.items():
            self.setData(key, val)
        return False


class TestCmdExcept(Command):
    def __init__(self):
        super(TestCmdExcept, self).__init__()

    def execute(self, context):
        for key, val in context.items():
            self.setData(key, val)
        raise AttributeError


class TestCommand(TestCase):
    def test_ioc(self):
        cmd = TestCmd()
        self.assertTrue(isinstance(cmd.ioc, GreaseContainer))

    def test_variable_storage_name(self):
        cmd = TestCmd()
        self.assertEqual(cmd.variable_storage.name, "TestCmd")

    def test_variable_storage(self):
        cmd = TestCmd()
        cmd.variable_storage.insert_one({'test': 'value'})
        self.assertEqual(cmd.variable_storage.find({'test': 'value'}).count(), 1)
        self.assertTrue(cmd.variable_storage.delete_one({'test': 'value'}))

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
        self.assertDictEqual(cmd.getData(), {'key': 'value'})

    def test_failed_cmd(self):
        cmd = TestCmdFail()
        cmd.safe_execute({})
        self.assertTrue(cmd.getExecVal())
        self.assertFalse(cmd.getRetVal())

    def test_except_cmd(self):
        cmd = TestCmdExcept()
        cmd.safe_execute({})
        self.assertFalse(cmd.getExecVal())
        self.assertFalse(cmd.getRetVal())
