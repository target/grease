from datetime import datetime, timedelta
from BaseDetectorClass import BaseDetector
import operator


class TimeDelta(BaseDetector):
    def __init__(self):
        self._result = {'result': False}
        self.operators = {
            '>': operator.gt,
            'gt': operator.gt,
            '<': operator.lt,
            'lt': operator.lt,
            '>=': operator.ge,
            'ge': operator.ge,
            '<=': operator.le,
            'le': operator.le,
            '=': operator.eq,
            'eq': operator.eq,
            '!=': operator.ne,
            'ne': operator.ne
        }
        self.units = {
            'seconds': 'seconds',
            'second': 'seconds',
            'sec': 'seconds',
            'minutes': 'minutes',
            'minute': 'minutes',
            'min': 'minutes',
            'hours': 'hours',
            'hour': 'hours',
            'hr': 'hours',
            'days': 'days',
            'day': 'days',
            'years': 'years',
            'year': 'years',
            'yr': 'years'
        }

    def param_compute(self, source, rules):
        rules_passed = 0
        rules_needed_to_pass = len(rules)

        for delta_obj in rules:
            # Validation and setup
            # Mandatory checks
            if 'field' not in delta_obj or 'date_format' not in delta_obj or 'delta' not in delta_obj or \
               'unit' not in delta_obj or 'direction' not in delta_obj or 'operator' not in delta_obj:
                    self._result['result'] = False
                    return

            source_date = str(source[delta_obj['field']])
            date_format = str(delta_obj['date_format'])
            delta = abs(int(delta_obj['delta']))

            if str(delta_obj['unit']) in self.units:
                unit = self.units[str(delta_obj['unit'])]
            else:
                self._result['result'] = False
                return

            if str(delta_obj['direction']) is 'future':
                direction = 1
            else:
                direction = -1

            if str(delta_obj['operator']) in self.operators:
                op = self.operators[str(delta_obj['operator'])]
            else:
                self._result['result'] = False
                return

            if 'date' in delta_obj:
                try:
                    rel_dt = datetime.strptime(str(delta_obj['date']), date_format) + timedelta(**{unit: delta}) * direction
                except ValueError:
                    self._result['result'] = False
                    return
            else:
                rel_dt = datetime.now() + timedelta(**{unit: delta}) * direction

            try:
                source_dt = datetime.strptime(source_date, date_format)
            except ValueError:
                self._result['result'] = False
                return

            # Comparison
            # If direction is future, we need to have the source_dt on the left side
            # If it's past, we need source_dt on the right
            if str(delta_obj['direction']) is 'future':
                date_compare = op(source_dt, rel_dt)
            else:
                date_compare = op(rel_dt, source_dt)

            if date_compare:
                rules_passed += 1
                if 'variable' in delta_obj:
                    if delta_obj['variable'] and 'variable_name' in delta_obj:
                        self._result[delta_obj['variable_name']] = source_date
            else:
                # field not found in source
                # time to fail out since not all parameters can be met
                self._result = {'result': False}
                return

        if rules_passed >= rules_needed_to_pass:
            self._result['result'] = True
        else:
            self._result = {'result': False}

        return

    def get_result(self):
        return self._result
