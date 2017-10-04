from .BaseDetectorClass import BaseDetector


class Exists(BaseDetector):
    def __init__(self):
        self._result = {'result': False}

    def param_compute(self, source, rules):
        rules_passed = 0
        rules_needed_to_pass = len(rules)

        for rule in rules:
            if 'field' not in rule:
                self._result['result'] = False
                return

            if rule['field'] in source:
                rules_passed += 1

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
