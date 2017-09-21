from unittest import TestCase
from tgt_grease_enterprise.Detectors import TimeDelta
from datetime import datetime, timedelta


class TestTimeDelta(TestCase):
    def _setup(self, delta, source_delta, direction='past'):
        self.TimeDelta = TimeDelta()

        if direction is 'past':
            dt = datetime.now() - timedelta(days=source_delta)
        else:
            dt = datetime.now() + timedelta(days=source_delta)

        date_string = dt.strftime("%Y-%m-%d")

        self.source_data = {
            "field": date_string
        }

        self.rules = [
            {
                "field": "field",
                "date_format": "%Y-%m-%d",
                "delta": delta,
                "unit": "days",
                "direction": direction,
                "operator": ">="
            }
        ]

    def _teardown(self):
        if self.TimeDelta:
            del self.TimeDelta
        if self.rules:
            del self.rules
        if self.source_data:
            del self.source_data

    def test_past_true(self):
        self._setup(delta=1, source_delta=3, direction='past')

        self.TimeDelta.param_compute(source=self.source_data, rules=self.rules)
        self.assertTrue(self.TimeDelta.get_result()['result'])
        self._teardown()

    def test_past_false(self):
        self._setup(delta=3, source_delta=1, direction='past')

        self.TimeDelta.param_compute(source=self.source_data, rules=self.rules)
        self.assertFalse(self.TimeDelta.get_result()['result'])
        self._teardown()

    def test_future_true(self):
        self._setup(delta=1, source_delta=3, direction='future')

        self.TimeDelta.param_compute(source=self.source_data, rules=self.rules)
        self.assertTrue(self.TimeDelta.get_result()['result'])
        self._teardown()

    def test_future_false(self):
        self._setup(delta=3, source_delta=1, direction='future')

        self.TimeDelta.param_compute(source=self.source_data, rules=self.rules)
        self.assertFalse(self.TimeDelta.get_result()['result'])
        self._teardown()

    def test_malformed_rule(self):
        self._setup(delta=1, source_delta=3)
        self.rules += {
            'biscuits': 'gravy'
        }

        self.TimeDelta.param_compute(source=self.source_data, rules=self.rules)
        self.assertFalse(self.TimeDelta.get_result()['result'])
        self._teardown()

    def test_bad_unit(self):
        self._setup(delta=1, source_delta=3)
        self.rules[0]['unit'] = 'eons'

        self.TimeDelta.param_compute(source=self.source_data, rules=self.rules)
        self.assertFalse(self.TimeDelta.get_result()['result'])
        self._teardown()

    def test_bad_operator(self):
        self._setup(delta=1, source_delta=3)
        self.rules[0]['operator'] = 'note'

        self.TimeDelta.param_compute(source=self.source_data, rules=self.rules)
        self.assertFalse(self.TimeDelta.get_result()['result'])
        self._teardown()

    def test_date_supplied(self):
        self._setup(delta=3, source_delta=3)
        self.source_data["field"] = "2017-08-20"
        self.rules[0]['date'] = "2017-08-24"

        self.TimeDelta.param_compute(source=self.source_data, rules=self.rules)
        self.assertTrue(self.TimeDelta.get_result()['result'])
        self._teardown()

    def test_format_mismatch(self):
        self._setup(delta=1, source_delta=3)
        self.rules[0]['date_format'] = '%y%m%d'

        self.TimeDelta.param_compute(source=self.source_data, rules=self.rules)
        self.assertFalse(self.TimeDelta.get_result()['result'])
        self._teardown()
