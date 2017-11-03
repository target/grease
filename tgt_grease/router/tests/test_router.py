from tgt_grease.router import GreaseRouter
from tgt_grease.router.Commands import help
import sys
from unittest import TestCase


class TestRouter(TestCase):
    def test_no_SubCommand(self):
        sys.argv = ['grease']
        cmd = GreaseRouter()
        self.assertEqual(cmd.run(), 1)

    def test_get_cli_args_without_command(self):
        sys.argv = ['grease', '--text=utf-8', '--opt', 'var', '--ver:var']
        rtr = GreaseRouter()
        cmd, context = rtr.get_arguments()
        self.assertIsNone(cmd)
        self.assertDictEqual(context, {'opt': 'var', 'text': 'utf-8', 'ver': 'var', 'grease_other_args': []})

    def test_get_cli_args_with_command_type1(self):
        sys.argv = ['grease', '--text=utf-8', '--opt', 'var', '--ver:var', 'help']
        rtr = GreaseRouter()
        cmd, context = rtr.get_arguments()
        self.assertTrue(isinstance(cmd, help))
        self.assertDictEqual(context, {'opt': 'var', 'text': 'utf-8', 'ver': 'var', 'grease_other_args': []})

    def test_get_cli_args_with_command_type2(self):
        sys.argv = ['grease', 'help', '--text=utf-8', '--opt', 'var', '--ver:var']
        rtr = GreaseRouter()
        cmd, context = rtr.get_arguments()
        self.assertTrue(isinstance(cmd, help))
        self.assertDictEqual(context, {'opt': 'var', 'text': 'utf-8', 'ver': 'var', 'grease_other_args': []})

    def test_get_cli_args_with_command_type3(self):
        sys.argv = ['grease', '--text=utf-8', 'help', '--opt', 'var', '--ver:var']
        rtr = GreaseRouter()
        cmd, context = rtr.get_arguments()
        self.assertTrue(isinstance(cmd, help))
        self.assertDictEqual(context, {'opt': 'var', 'text': 'utf-8', 'ver': 'var', 'grease_other_args': []})

    def test_get_cli_args_with_command_type4(self):
        sys.argv = ['grease', '--text=utf-8', '--opt', 'var', 'help', '--ver:var']
        rtr = GreaseRouter()
        cmd, context = rtr.get_arguments()
        self.assertTrue(isinstance(cmd, help))
        self.assertDictEqual(context, {'opt': 'var', 'text': 'utf-8', 'ver': 'var', 'grease_other_args': []})

    def test_get_cli_args_with_command_type5(self):
        sys.argv = ['grease', 'help', '--text=utf-8', '--opt', 'var', '--ver:var', 'install']
        rtr = GreaseRouter()
        cmd, context = rtr.get_arguments()
        self.assertTrue(isinstance(cmd, help))
        self.assertDictEqual(context, {'opt': 'var', 'text': 'utf-8', 'ver': 'var', 'grease_other_args': ['install']})

    def test_get_cli_args_with_command_type6(self):
        sys.argv = ['grease', 'help', 'install', '--text=utf-8', '--opt', 'var', '--ver:var']
        rtr = GreaseRouter()
        cmd, context = rtr.get_arguments()
        self.assertTrue(isinstance(cmd, help))
        self.assertDictEqual(context, {'opt': 'var', 'text': 'utf-8', 'ver': 'var', 'grease_other_args': ['install']})

    def test_get_cli_args_with_command_type7(self):
        sys.argv = ['grease', 'help', '--text=utf-8', 'install', '--opt', 'var', '--ver:var']
        rtr = GreaseRouter()
        cmd, context = rtr.get_arguments()
        self.assertTrue(isinstance(cmd, help))
        self.assertDictEqual(context, {'opt': 'var', 'text': 'utf-8', 'ver': 'var', 'grease_other_args': ['install']})

    def test_get_cli_args_with_command_type8(self):
        sys.argv = ['grease', 'help', 'install']
        rtr = GreaseRouter()
        cmd, context = rtr.get_arguments()
        self.assertTrue(isinstance(cmd, help))
        self.assertDictEqual(context, {'grease_other_args': ['install']})

    def test_get_cli_args_with_command_type9(self):
        sys.argv = ['grease', 'help', 'install', 'to-do-stuff']
        rtr = GreaseRouter()
        cmd, context = rtr.get_arguments()
        self.assertTrue(isinstance(cmd, help))
        self.assertDictEqual(context, {'grease_other_args': ['install', 'to-do-stuff']})

    def test_get_cli_args_with_command_type10(self):
        sys.argv = ['grease', 'help', 'install', 'to-do-stuff', '--foreground']
        rtr = GreaseRouter()
        cmd, context = rtr.get_arguments()
        self.assertTrue(isinstance(cmd, help))
        self.assertDictEqual(context, {'foreground': True, 'grease_other_args': ['install', 'to-do-stuff']})

    def test_get_cli_args_with_command_type11(self):
        sys.argv = ['grease', 'help', '--test=var', '--foreground', '--test1:var1', '--test2', 'var2', 'install']
        rtr = GreaseRouter()
        cmd, context = rtr.get_arguments()
        self.assertTrue(isinstance(cmd, help))
        self.assertDictEqual(
            {'foreground': True, 'test': 'var', 'test1': 'var1', 'test2': 'var2', 'grease_other_args': ['install']},
            context
        )

    def test_get_cli_args_with_command_type12(self):
        sys.argv = ['grease', 'help', '--test=var', '--foreground', '--test1:var1', '--test2', 'var2']
        rtr = GreaseRouter()
        cmd, context = rtr.get_arguments()
        self.assertTrue(isinstance(cmd, help))
        self.assertTrue(
            context,
            {'foreground': True, 'test': 'var', 'test1': 'var1', 'test2': 'var2', 'grease_other_args': []}
        )

    def test_get_cli_args_with_command_type13(self):
        sys.argv = ['grease', '--foreground', 'help', '--test=var', '--test1:var1', '--test2', 'var2']
        rtr = GreaseRouter()
        cmd, context = rtr.get_arguments()
        self.assertTrue(isinstance(cmd, help))
        self.assertTrue(
            context,
            {'foreground': True, 'test': 'var', 'test1': 'var1', 'test2': 'var2', 'grease_other_args': []}
        )
