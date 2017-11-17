from unittest import TestCase
from tgt_grease.enterprise.Sources import sql_source


class TestSQLSource(TestCase):

    def test_type(self):
        inst = sql_source()
        self.assertTrue(isinstance(inst, sql_source))
