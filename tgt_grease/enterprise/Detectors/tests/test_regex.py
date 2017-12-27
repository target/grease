from unittest import TestCase
from tgt_grease.enterprise.Detectors import Regex


class TestRegex(TestCase):

    def test_emptyList(self):
        r = Regex()
        state, data = r.processObject({}, [])
        self.assertFalse(state)
        self.assertFalse(data)

    def test_valid(self):
        r = Regex()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': 5
            },
            [
                {
                    'field': 'test',
                    'pattern': '.*',
                    'variable': True,
                    'variable_name': 'test1'
                },
                {
                    'field': 'ver',
                    'pattern': '.*(var).*'
                }
            ]
        )
        self.assertTrue(state)
        self.assertEqual(data.get('test1'), ['data', ''])

    def test_valid_no_variables(self):
        r = Regex()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': 5
            },
            [
                {
                    'field': 'test',
                    'pattern': '.*',
                },
                {
                    'field': 'ver',
                    'pattern': '.*(var).*'
                },
                {
                    'field': 'data',
                    'pattern': '.*'
                }
            ]
        )
        self.assertTrue(state)
        self.assertEqual(len(data), 0)

    def test_invalid_config(self):
        r = Regex()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': 5
            },
            [
                {
                },
                {
                    'pattern': '.*(var).*'
                },
                {
                    'field': 'data',
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_failed_regex(self):
        r = Regex()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': 5
            },
            [
                {
                    'pattern': '.*(var).*'
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_bad_source(self):
        r = Regex()
        state, data = r.processObject(
            [],
            [
                {
                    'pattern': '.*(var).*'
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_bad_config(self):
        r = Regex()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': 5
            },
            {}
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_empty_result(self):
        r = Regex()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': 5
            },
            [
                {
                    'field': 'test',
                    'pattern': '.*(var).*'
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_field_not_exist(self):
        r = Regex()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': 5
            },
            [
                {
                    'field': 'test1',
                    'pattern': '.*(var).*'
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_bad_block(self):
        r = Regex()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': 5
            },
            [
                []
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)
