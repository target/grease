from .BaseDetectorClass import BaseDetector
from datetime import datetime


# Basic DateRange Detector Config
# ...
# "DateRange": [
#    {
#       "field": "my_field", <- Mandatory
#       "min": 1999-12-31, <- Optional if max is used
#       "max": 2017-08-30, <- Optional if min is used
#       "date_format": "%Y-%m-%d" <- Format, via https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
#       "variable": True, <- Optional Assignment Parameter
#       "variable_name": "my_field" <- Optional Assignment Parameter
#    }
# ]
#
# ...


class DateRange(BaseDetector):
    def __init__(self):
        self._result = {'result': False}

    def param_compute(self, source, rules):
        rules_needed_to_pass = len(rules)
        rules_passed = 0

        for range_conf in rules:
            if 'field' not in range_conf or 'date_format' not in range_conf:
                self._result = {'result': False}
                return

            if range_conf['field'] in source:
                range_compare = False
                date_format = str(range_conf['date_format'])

                try:
                    source_dt = datetime.strptime(str(source[range_conf['field']]), date_format)
                    if 'max' in range_conf and 'min' in range_conf:
                        max_dt = datetime.strptime(str(range_conf['max']), date_format)
                        min_dt = datetime.strptime(str(range_conf['min']), date_format)
                        range_compare = min_dt <= source_dt <= max_dt
                    elif 'min' in range_conf:
                        min_dt = datetime.strptime(str(range_conf['min']), date_format)
                        range_compare = min_dt <= source_dt
                    elif 'max' in range_conf:
                        max_dt = datetime.strptime(str(range_conf['max']), date_format)
                        range_compare = source_dt <= max_dt
                    else:
                        # invalid config no range parameters set
                        self._result = {'result': False}
                        return
                except ValueError:
                    # Something went wrong with parsing, likely something with the date format
                    self._result = {'result': False}
                    return

                if range_compare:
                    rules_passed += 1
                    self._result['result'] = True
                    if 'variable' in range_conf:
                        if range_conf['variable'] and 'variable_name' in range_conf:
                            self._result[range_conf['variable_name']] = str(source[range_conf['field']])
            else:
                # field not found in source
                # time to fail out since not all range parameters can be met
                self._result = {'result': False}
                return

        if rules_needed_to_pass == rules_passed:
            return
        else:
            self._result = {'result': False}
            return

    def get_result(self):
        return self._result