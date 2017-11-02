from tgt_grease.router import GreaseRouter
from tgt_grease import help
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
        self.assertDictEqual(context, {'opt': 'var', 'text': 'utf-8', 'ver': 'var'})

    def test_get_cli_args_with_command_type1(self):
        sys.argv = ['grease', '--text=utf-8', '--opt', 'var', '--ver:var', 'help']
        rtr = GreaseRouter()
        cmd, context = rtr.get_arguments()
        self.assertTrue(isinstance(cmd, help))
        self.assertDictEqual(context, {'opt': 'var', 'text': 'utf-8', 'ver': 'var'})

    def test_get_cli_args_with_command_type2(self):
        sys.argv = ['grease', 'help', '--text=utf-8', '--opt', 'var', '--ver:var']
        rtr = GreaseRouter()
        cmd, context = rtr.get_arguments()
        self.assertTrue(isinstance(cmd, help))
        self.assertDictEqual(context, {'opt': 'var', 'text': 'utf-8', 'ver': 'var'})

    def test_get_cli_args_with_command_type3(self):
        sys.argv = ['grease', '--text=utf-8', 'help', '--opt', 'var', '--ver:var']
        rtr = GreaseRouter()
        cmd, context = rtr.get_arguments()
        self.assertTrue(isinstance(cmd, help))
        self.assertDictEqual(context, {'opt': 'var', 'text': 'utf-8', 'ver': 'var'})

    def test_get_cli_args_with_command_type4(self):
        sys.argv = ['grease', '--text=utf-8', '--opt', 'var', 'help', '--ver:var']
        rtr = GreaseRouter()
        cmd, context = rtr.get_arguments()
        self.assertTrue(isinstance(cmd, help))
        self.assertDictEqual(context, {'opt': 'var', 'text': 'utf-8', 'ver': 'var'})
