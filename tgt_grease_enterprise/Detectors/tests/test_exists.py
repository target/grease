from unittest import TestCase
from tgt_grease_enterprise.Detectors import Exists


class TestExists(TestCase):
    def _setup(self):
        self.Exists = Exists()

    def _teardown(self):
        if self.Exists:
            del self.Exists

    def test_exists(self):
        self._setup()
        source_data = {
            'key': 'value'
        }

        rules = [
            {
                'field': 'key'
            }
        ]

        self.Exists.param_compute(source=source_data, rules=rules)
        self.assertTrue(self.Exists.get_result()['result'])
        self._teardown()

    def test_does_not_exist(self):
        self._setup()
        source_data = {
            'key': 'value'
        }

        rules = [
            {
                'field': 'other_key'
            }
        ]

        self.Exists.param_compute(source=source_data, rules=rules)
        self.assertFalse(self.Exists.get_result()['result'])
        self._teardown()

    def test_malformed_rule(self):
        self._setup()
        source_data = {
            'key': 'value'
        }

        rules = [
            {
                'biscuits': 'gravy'
            }
        ]

        self.Exists.param_compute(source=source_data, rules=rules)
        self.assertFalse(self.Exists.get_result()['result'])
        self._teardown()
        
    def test_variable_set(self):
        self._setup()
        source_data = {
            'key': 'value'
        }

        rules = [
            {
                'field': 'key',
                'variable': True,
                'variable_name': 'var'
            }
        ]
        
        self.Exists.param_compute(source=source_data, rules=rules)
        self.assertTrue(self.Exists.get_result()['result'])
        self.assertEqual(self.Exists.get_result()['var'], 'value')
        self._teardown()

