from unittest import TestCase
from tgt_grease.enterprise.Detectors import Exists


class TestExists(TestCase):

    def test_emptyList(self):
        e = Exists()
        state, data = e.processObject({}, [])
        self.assertFalse(state)
        self.assertFalse(data)

    def test_valid(self):
        e = Exists()
        state, data = e.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': 5
            },
            [
                {
                    'field': 'test',
                    'variable': True,
                    'variable_name': 'test1'
                },
                {
                    'field': 'ver',
                }
            ]
        )
        self.assertTrue(state)
        self.assertEqual(data.get('test1'), 'data')

    def test_empty_field(self):
        e = Exists()
        state, data = e.processObject(
            {
                'test': u'data',
                'ver': '',
                'data': 5
            },
            [
                {
                    'field': 'ver',
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_valid_no_variables(self):
        e = Exists()
        state, data = e.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': 5
            },
            [
                {
                    'field': 'test'
                },
                {
                    'field': 'ver'
                },
                {
                    'field': 'data'
                }
            ]
        )
        self.assertTrue(state)
        self.assertEqual(len(data), 0)

    def test_invalid_config(self):
        e = Exists()
        state, data = e.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': 5
            },
            [
                {
                },
                {
                    'field': 'data',
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_failed_exists(self):
        e = Exists()
        state, data = e.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': 5
            },
            [
                {
                    'pattern': 'test1'
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_bad_source(self):
        e = Exists()
        state, data = e.processObject(
            [],
            [
                {
                    'field': 'test'
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_bad_config(self):
        e = Exists()
        state, data = e.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': 5
            },
            {}
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_bad_block(self):
        e = Exists()
        state, data = e.processObject(
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
