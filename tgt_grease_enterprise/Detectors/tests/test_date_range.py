from unittest import TestCase
from tgt_grease_enterprise.Detectors import DateRange


class TestDateRange(TestCase):
    def _setup(self, source_date, min_date='', max_date=''):
        self.DateRange = DateRange()

        self.source_data = {
            "field": source_date
        }

        self.rules = [
            {
                "field": "field",
                "date_format": "%Y-%m-%d",
                "operator": ">="
            }
        ]

        if min_date:
            self.rules[0]['min'] = min_date
        if max_date:
            self.rules[0]['max'] = max_date

    def _teardown(self):
        if self.DateRange:
            del self.DateRange
        if self.rules:
            del self.rules
        if self.source_data:
            del self.source_data

    def test_min_and_max_true(self):
        self._setup(source_date='2017-05-31', min_date='2017-04-19', max_date='2017-08-25')

        self.DateRange.param_compute(source=self.source_data, rules=self.rules)
        self.assertTrue(self.DateRange.get_result()['result'])
        self._teardown()

    def test_min_and_max_false(self):
        self._setup(source_date='2017-04-19', min_date='2017-05-31', max_date='2017-08-25')

        self.DateRange.param_compute(source=self.source_data, rules=self.rules)
        self.assertFalse(self.DateRange.get_result()['result'])
        self._teardown()

    def test_min_true(self):
        self._setup(source_date='2017-05-31', min_date='2017-04-19')

        self.DateRange.param_compute(source=self.source_data, rules=self.rules)
        self.assertTrue(self.DateRange.get_result()['result'])
        self._teardown()

    def test_min_false(self):
        self._setup(source_date='2017-05-31', min_date='2017-08-25')

        self.DateRange.param_compute(source=self.source_data, rules=self.rules)
        self.assertFalse(self.DateRange.get_result()['result'])
        self._teardown()

    def test_max_true(self):
        self._setup(source_date='2017-05-31', max_date='2017-08-25')

        self.DateRange.param_compute(source=self.source_data, rules=self.rules)
        self.assertTrue(self.DateRange.get_result()['result'])
        self._teardown()

    def test_max_false(self):
        self._setup(source_date='2017-05-31', max_date='2017-04-19')

        self.DateRange.param_compute(source=self.source_data, rules=self.rules)
        self.assertFalse(self.DateRange.get_result()['result'])
        self._teardown()

    def test_no_max_min(self):
        self._setup(source_date='2017-05-31')

        self.DateRange.param_compute(source=self.source_data, rules=self.rules)
        self.assertFalse(self.DateRange.get_result()['result'])
        self._teardown()

    def test_malformed_rule(self):
        self._setup(source_date='2017-05-31', min_date='2017-04-19', max_date='2017-08-25')
        self.rules.append({
            'biscuits': 'gravy'
        })

        self.DateRange.param_compute(source=self.source_data, rules=self.rules)
        self.assertFalse(self.DateRange.get_result()['result'])
        self._teardown()

    def test_format_mismatch(self):
        self._setup(source_date='2017-05-31', min_date='2017-04-19', max_date='2017-08-25')
        self.rules[0]['date_format'] = '%y%m%d'

        self.DateRange.param_compute(source=self.source_data, rules=self.rules)
        self.assertFalse(self.DateRange.get_result()['result'])
        self._teardown()
