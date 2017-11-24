from unittest import TestCase
from tgt_grease.enterprise.Detectors import DateDelta
import datetime


class TestDateDelta(TestCase):

    def test_range_compare_pass_lt(self):
        r = DateDelta()
        compare_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        self.assertTrue(r.timeCompare(
                compare_date,
                {
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'future',
                    'operator': '<',
                    'format': '%Y-%m-%d'
                }
            )
        )
        self.assertTrue(r.timeCompare(
                (
                    datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                    + datetime.timedelta(days=1) * -1
                ).strftime('%Y-%m-%d'),
                {
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'past',
                    'operator': '=',
                    'format': '%Y-%m-%d'
                }
            )
        )

    def test_range_compare_pass_lt_with_date(self):
        r = DateDelta()
        compare_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        self.assertTrue(r.timeCompare(
                compare_date,
                {
                    'date': compare_date,
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'future',
                    'operator': '<',
                    'format': '%Y-%m-%d'
                }
            )
        )
        self.assertTrue(r.timeCompare(
                (
                    datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                    + datetime.timedelta(days=1) * -1
                ).strftime('%Y-%m-%d'),
                {
                    'date': compare_date,
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'past',
                    'operator': '=',
                    'format': '%Y-%m-%d'
                }
            )
        )

    def test_range_compare_pass_lteq(self):
        r = DateDelta()
        compare_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        self.assertTrue(r.timeCompare(
                compare_date,
                {
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'future',
                    'operator': '<=',
                    'format': '%Y-%m-%d'
                }
            )
        )
        self.assertTrue(r.timeCompare(
                (
                    datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                    + datetime.timedelta(days=1) * -1
                ).strftime('%Y-%m-%d'),
                {
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'past',
                    'operator': '<=',
                    'format': '%Y-%m-%d'
                }
            )
        )

    def test_range_compare_pass_lteq_with_date(self):
        r = DateDelta()
        compare_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        self.assertTrue(r.timeCompare(
                compare_date,
                {
                    'date': compare_date,
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'future',
                    'operator': '<=',
                    'format': '%Y-%m-%d'
                }
            )
        )
        self.assertTrue(r.timeCompare(
                (
                    datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                    + datetime.timedelta(days=1) * -1
                ).strftime('%Y-%m-%d'),
                {
                    'date': compare_date,
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'past',
                    'operator': '<=',
                    'format': '%Y-%m-%d'
                }
            )
        )

    def test_range_compare_pass_gt(self):
        r = DateDelta()
        compare_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        compare_date = (
                    datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                    + datetime.timedelta(days=2)
                ).strftime('%Y-%m-%d')
        self.assertTrue(r.timeCompare(
                compare_date,
                {
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'future',
                    'operator': '>',
                    'format': '%Y-%m-%d'
                }
            )
        )

    def test_range_compare_pass_gt_with_date(self):
        r = DateDelta()
        compare_date1 = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        compare_date = (
                    datetime.datetime.strptime(compare_date1, '%Y-%m-%d')
                    + datetime.timedelta(days=2)
                ).strftime('%Y-%m-%d')
        self.assertTrue(r.timeCompare(
                compare_date,
                {
                    'date': compare_date1,
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'future',
                    'operator': '>',
                    'format': '%Y-%m-%d'
                }
            )
        )

    def test_range_compare_pass_gteq(self):
        r = DateDelta()
        compare_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        compare_date = (
                    datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                    + datetime.timedelta(days=2)
                ).strftime('%Y-%m-%d')
        self.assertTrue(r.timeCompare(
                compare_date,
                {
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'future',
                    'operator': '>=',
                    'format': '%Y-%m-%d'
                }
            )
        )

    def test_range_compare_pass_gteq_with_date(self):
        r = DateDelta()
        compare_date1 = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        compare_date = (
                    datetime.datetime.strptime(compare_date1, '%Y-%m-%d')
                    + datetime.timedelta(days=2)
                ).strftime('%Y-%m-%d')
        self.assertTrue(r.timeCompare(
                compare_date,
                {
                    'date': compare_date1,
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'future',
                    'operator': '>=',
                    'format': '%Y-%m-%d'
                }
            )
        )

    def test_range_compare_pass_neq(self):
        r = DateDelta()
        compare_date1 = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        compare_date = (
                    datetime.datetime.strptime(compare_date1, '%Y-%m-%d')
                    + datetime.timedelta(days=2)
                ).strftime('%Y-%m-%d')
        self.assertTrue(r.timeCompare(
                compare_date,
                {
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'future',
                    'operator': '!=',
                    'format': '%Y-%m-%d'
                }
            )
        )
        self.assertTrue(r.timeCompare(
                (
                    datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                    + datetime.timedelta(days=1) * -1
                ).strftime('%Y-%m-%d'),
                {
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'past',
                    'operator': '!=',
                    'format': '%Y-%m-%d'
                }
            )
        )

    def test_range_compare_bad_operator(self):
        r = DateDelta()
        compare_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        self.assertFalse(r.timeCompare(
                compare_date,
                {
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'future',
                    'operator': '<>',
                    'format': '%Y-%m-%d'
                }
            )
        )
        self.assertFalse(r.timeCompare(
                (
                    datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                    + datetime.timedelta(days=1) * -1
                ).strftime('%Y-%m-%d'),
                {
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'past',
                    'operator': '<>',
                    'format': '%Y-%m-%d'
                }
            )
        )

    def test_range_compare_bad_direction(self):
        r = DateDelta()
        compare_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        self.assertFalse(r.timeCompare(
                compare_date,
                {
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'cats',
                    'operator': '<',
                    'format': '%Y-%m-%d'
                }
            )
        )
        self.assertFalse(r.timeCompare(
                (
                    datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                    + datetime.timedelta(days=1) * -1
                ).strftime('%Y-%m-%d'),
                {
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'dogs',
                    'operator': '<',
                    'format': '%Y-%m-%d'
                }
            )
        )

    def test_range_compare_value_error(self):
        r = DateDelta()
        compare_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        self.assertFalse(r.timeCompare(
                compare_date,
                {
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'future',
                    'operator': '<>',
                    'format': 'Y%-%m-%d'
                }
            )
        )
        self.assertFalse(r.timeCompare(
                (
                    datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                    + datetime.timedelta(days=1) * -1
                ).strftime('%Y-%m-%d'),
                {
                    'delta': 'days',
                    'delta_value': 1,
                    'direction': 'past',
                    'operator': '<>',
                    'format': 'Y%-%m-%d'
                }
            )
        )

    def test_good_config(self):
        r = DateDelta()
        compare_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        result, data = r.processObject(
                {
                    'data': compare_date
                },
                [
                    {
                        'field': 'data',
                        'delta': 'days',
                        'delta_value': 1,
                        'direction': 'future',
                        'operator': '<',
                        'format': '%Y-%m-%d',
                        'variable': True,
                        'variable_name': 'data'
                    }
                ]
            )
        self.assertTrue(result)
        self.assertEqual(data.get('data'), compare_date)
        result, data = r.processObject(
                {
                    'data': compare_date
                },
                [
                    {
                        'field': 'data',
                        'delta': 'days',
                        'delta_value': 1,
                        'direction': 'future',
                        'operator': '<',
                        'format': '%Y-%m-%d'
                    }
                ]
            )
        self.assertTrue(result)
        self.assertFalse(data)

    def test_bad_config(self):
        r = DateDelta()
        compare_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        result, data = r.processObject(
                {
                    'data': compare_date
                },
                [
                    {
                        'field': 'data',
                        'delta': 'day',
                        'delta_value': 1,
                        'direction': 'future',
                        'operator': '<',
                        'format': '%Y-%m-%d'
                    }
                ]
            )
        self.assertFalse(result)
        self.assertFalse(data)

    def test_field_not_exist(self):
        r = DateDelta()
        compare_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        result, data = r.processObject(
                {
                },
                [
                    {
                        'field': 'data',
                        'delta': 'day',
                        'delta_value': 1,
                        'direction': 'future',
                        'operator': '<',
                        'format': '%Y-%m-%d'
                    }
                ]
            )
        self.assertFalse(result)
        self.assertFalse(data)

    def test_bad_field(self):
        r = DateDelta()
        compare_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        result, data = r.processObject(
                {
                    'data': False
                },
                [
                    {
                        'field': 'data',
                        'delta': 'day',
                        'delta_value': 1,
                        'direction': 'future',
                        'operator': '<',
                        'format': '%Y-%m-%d'
                    }
                ]
            )
        self.assertFalse(result)
        self.assertFalse(data)

    def test_pass_out_of_range(self):
        r = DateDelta()
        compare_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        result, data = r.processObject(
                {
                    'data': compare_date
                },
                [
                    {
                        'field': 'data',
                        'delta': 'weeks',
                        'delta_value': 2,
                        'direction': 'past',
                        'operator': '<',
                        'format': '%Y-%m-%d',
                        'variable': True,
                        'variable_name': 'data'
                    }
                ]
            )
        self.assertFalse(result)
        self.assertFalse(data)
