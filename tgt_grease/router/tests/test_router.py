from tgt_grease.router import GreaseRouter
import sys
from unittest import TestCase


class TestRouter(TestCase):
    def test_no_SubCommand(self):
        sys.argv = ['grease']
        cmd = GreaseRouter()
        self.assertEqual(cmd.run(), 1)

    def test_get_cli_args(self):
        sys.argv = ['grease', '--text=utf-8', '--opt', 'var', '--ver:var']
        self.assertDictEqual(GreaseRouter.get_arguments(), {'opt': 'var', 'text': 'utf-8', 'ver': 'var'})
