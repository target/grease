from BaseDetectorClass import BaseDetector


# Basic Range Detector Config
# ...
# "Range": [
#    {
#       "field": "my_field", <- Mandatory
#       "min": 10, <- Optional if max is used
#       "max": 100, <- Optional if min is used
#       "variable": True, <- Optional Assignment Parameter
#       "variable_name": "my_field" <- Optional Assignment Parameter
#    }
# ]
#
# ...


class Range(BaseDetector):
    def __init__(self):
        self._result = {'result': False}

    def param_compute(self, source, rules):
        rules_needed_to_pass = len(rules)
        rules_passed = 0
        for range_conf in rules:
            if range_conf['field'] in source:
                range_compare = False
                if 'max' in range_conf and 'min' in range_conf:
                    if int(range_conf['max']) < int(source[range_conf['field']]) \
                            or int(range_conf['min']) > int(source[range_conf['field']]):
                        range_compare = True
                elif 'min' in range_conf:
                    if int(range_conf['min']) > int(source[range_conf['field']]):
                        range_compare = True
                elif 'max' in range_conf:
                    if int(range_conf['max']) < int(source[range_conf['field']]):
                        range_compare = True
                else:
                    # invalid config no range parameters set
                    self._result = {'result': False}
                    return
                if range_compare:
                    rules_passed += 1
                    self._result['result'] = True
                    if 'variable' in range_conf:
                        if range_conf['variable'] and 'variable_name' in range_conf:
                            self._result[range_conf['variable_name']] = int(source[range_conf['field']])
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
