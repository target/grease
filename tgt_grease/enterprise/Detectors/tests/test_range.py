from unittest import TestCase
from tgt_grease.enterprise.Detectors import Range


class TestRange(TestCase):

    def test_range_compare_min_pass(self):
        r = Range()
        self.assertTrue(r.range_compare(5, {'min': 4}))
        self.assertTrue(r.range_compare(4.1, {'min': 4.0}))

    def test_range_compare_min_fail(self):
        r = Range()
        self.assertFalse(r.range_compare(3, {'min': 4}))
        self.assertFalse(r.range_compare(3.9, {'min': 4.0}))

    def test_range_compare_max_pass(self):
        r = Range()
        self.assertTrue(r.range_compare(3, {'max': 4}))
        self.assertTrue(r.range_compare(3.9, {'max': 4.0}))

    def test_range_compare_max_fail(self):
        r = Range()
        self.assertFalse(r.range_compare(5, {'max': 4}))
        self.assertFalse(r.range_compare(4.1, {'max': 4.0}))

    def test_range_compare_min_and_max_pass(self):
        r = Range()
        self.assertTrue(r.range_compare(3, {'max': 4, 'min': 1}))
        self.assertTrue(r.range_compare(3.9, {'max': 4.0, 'min': 1}))

    def test_range_compare_min_and_max_fail(self):
        r = Range()
        self.assertFalse(r.range_compare(5, {'max': 4, 'min': 1}))
        self.assertFalse(r.range_compare(4.1, {'max': 4.0, 'min': 1}))

    def test_range_compare_no_min_or_max(self):
        r = Range()
        self.assertFalse(r.range_compare(5, {}))

    def test_range_compare_bad_field_type(self):
        r = Range()
        self.assertFalse(r.range_compare('cats', {'max': 4, 'min': 1}))

    def test_range_compare_bad_min_or_max(self):
        r = Range()
        self.assertFalse(r.range_compare(3, {'min': 'cat'}))
        self.assertFalse(r.range_compare(3.9, {'min': 'dog'}))
        self.assertFalse(r.range_compare(5, {'max': 'cat'}))
        self.assertFalse(r.range_compare(4.1, {'max': 'dog'}))
        self.assertFalse(r.range_compare(5, {'max': 'cat', 'min': 'bagel'}))
        self.assertFalse(r.range_compare(4.1, {'max': 'dog', 'min': 'bagel'}))

    def test_emptyList(self):
        r = Range()
        state, data = r.processObject({}, [])
        self.assertFalse(state)
        self.assertFalse(data)

    def test_valid(self):
        r = Range()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': 5
            },
            [
                {
                    'field': 'data',
                    'min': 4,
                    'variable': True,
                    'variable_name': 'data'
                }
            ]
        )
        self.assertTrue(state)
        self.assertEqual(data.get('data'), 5)

    def test_valid_no_variables(self):
        r = Range()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': 5
            },
            [
                {
                    'field': 'data',
                    'min': 5,
                }
            ]
        )
        self.assertTrue(state)
        self.assertEqual(len(data), 0)

    def test_invalid_config(self):
        r = Range()
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
        r = Range()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': 5
            },
            [
                {
                    'max': 4
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_bad_source(self):
        r = Range()
        state, data = r.processObject(
            [],
            [
                {
                    'field': 'data',
                    'min': 3
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_bad_config(self):
        r = Range()
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
        r = Range()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': 5
            },
            [
                {
                    'field': 'data',
                    'min': 7
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_field_not_exist(self):
        r = Range()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': 5
            },
            [
                {
                    'field': 'data2',
                    'min': 6
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_field_false(self):
        r = Range()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': False
            },
            [
                {
                    'field': 'data',
                    'min': 6
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_bad_block(self):
        r = Range()
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
