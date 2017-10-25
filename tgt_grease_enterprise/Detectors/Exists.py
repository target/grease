from .BaseDetectorClass import BaseDetector


# Basic Exists Detector Config
# ...
# "exists": [
#    {
#       "field": "my_field", <- Mandatory
#       "variable": True, <- Optional Assignment Parameter
#       "variable_name": "my_field" <- Optional Assignment Parameter
#    }
# ]
#
# ...


class Exists(BaseDetector):
    def __init__(self):
        self._result = {'result': False}

    def param_compute(self, source, rules):
        rules_passed = 0
        rules_needed_to_pass = len(rules)

        for rule in rules:
            # Malformed rule; need 'field'
            if 'field' not in rule:
                self._result['result'] = False
                return

            # If the source contains the field, we passed
            if rule['field'] in source:
                rules_passed += 1

                # If we want to capture the field as a variable, add it to the final result
                if 'variable' in rule:
                    if rule['variable'] and 'variable_name' in rule:
                        self._result[rule['variable_name']] = source[rule['field']]
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
