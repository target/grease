from unittest import TestCase
from tgt_grease.enterprise.Detectors import DateRange


class TestDateRange(TestCase):

    def test_range_compare_min_pass(self):
        r = DateRange()
        self.assertTrue(r.timeCompare('2017-11-24', {'min': '2017-11-24', 'format': '%Y-%m-%d'}))

    def test_range_compare_min_fail(self):
        r = DateRange()
        self.assertFalse(r.timeCompare('2017-11-24', {'min': '2017-11-25', 'format': '%Y-%m-%d'}))

    def test_range_compare_max_pass(self):
        r = DateRange()
        self.assertTrue(r.timeCompare('2017-11-24', {'max': '2017-11-25', 'format': '%Y-%m-%d'}))

    def test_range_compare_max_fail(self):
        r = DateRange()
        self.assertFalse(r.timeCompare('2017-11-24', {'max': '2017-11-23', 'format': '%Y-%m-%d'}))

    def test_range_compare_min_and_max_pass(self):
        r = DateRange()
        self.assertTrue(r.timeCompare('2017-11-25', {'min': '2017-11-24', 'max': '2017-11-26', 'format': '%Y-%m-%d'}))

    def test_range_compare_min_and_max_fail(self):
        r = DateRange()
        self.assertFalse(r.timeCompare('2017-11-32', {'min': '2017-11-24', 'max': '2017-11-26', 'format': '%Y-%m-%d'}))

    def test_range_compare_no_min_or_max(self):
        r = DateRange()
        self.assertFalse(r.timeCompare('2017-11-24', {}))

    def test_range_compare_bad_field_type(self):
        r = DateRange()
        self.assertFalse(r.timeCompare('cats', {'min': '2017-11-24', 'max': '2017-11-26', 'format': '%Y-%m-%d'}))

    def test_range_compare_bad_min_or_max(self):
        r = DateRange()
        self.assertFalse(r.timeCompare('2017-11-23', {'min': '2017-11-24', 'format': '%Y-%m-%d'}))
        self.assertFalse(r.timeCompare('2017-11-25', {'max': '2017-11-24', 'format': '%Y-%m-%d'}))
        self.assertFalse(r.timeCompare('2017-11-27', {'min': '2017-11-24', 'max': '2017-11-26', 'format': '%Y-%m-%d'}))

    def test_emptyList(self):
        r = DateRange()
        state, data = r.processObject({}, [])
        self.assertFalse(state)
        self.assertFalse(data)

    def test_valid(self):
        r = DateRange()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': '2017-11-24'
            },
            [
                {
                    'field': 'data',
                    'min': '2017-11-24',
                    'format': '%Y-%m-%d',
                    'variable': True,
                    'variable_name': 'data'
                }
            ]
        )
        self.assertTrue(state)
        self.assertEqual(data.get('data'), '2017-11-24')

    def test_valid_no_variables(self):
        r = DateRange()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': '2017-11-24'
            },
            [
                {
                    'field': 'data',
                    'min': '2017-11-24',
                    'format': '%Y-%m-%d'
                }
            ]
        )
        self.assertTrue(state)
        self.assertEqual(len(data), 0)

    def test_invalid_config(self):
        r = DateRange()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': '2017-11-24'
            },
            [
                {
                    'field': 'data',
                    'min': '2017-11-24'
                    # no format
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_bad_source(self):
        r = DateRange()
        state, data = r.processObject(
            [],
            [
                {
                    'field': 'data',
                    'min': '2017-11-24',
                    'format': '%Y-%m-%d',
                    'variable': True,
                    'variable_name': 'data'
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_bad_config(self):
        r = DateRange()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': '2017-11-24'
            },
            {}
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_empty_result(self):
        r = DateRange()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': '2017-11-23'
            },
            [
                {
                    'field': 'data',
                    'min': '2017-11-24',
                    'format': '%Y-%m-%d',
                    'variable': True,
                    'variable_name': 'data'
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_field_not_exist(self):
        r = DateRange()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': '2017-11-24'
            },
            [
                {
                    'field': 'data1',
                    'min': '2017-11-24',
                    'format': '%Y-%m-%d',
                    'variable': True,
                    'variable_name': 'data'
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_field_false(self):
        r = DateRange()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': False
            },
            [
                {
                    'field': 'data',
                    'min': '2017-11-24',
                    'format': '%Y-%m-%d',
                    'variable': True,
                    'variable_name': 'data'
                }
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)

    def test_bad_block(self):
        r = DateRange()
        state, data = r.processObject(
            {
                'test': u'data',
                'ver': 'var',
                'data': '2017-11-24'
            },
            [
                []
            ]
        )
        self.assertFalse(state)
        self.assertEqual(len(data), 0)
