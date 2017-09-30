from .BaseDetectorClass import BaseDetector
import re

# Basic Regex Detector Config
# ...
# "regex": [
#    {
#       "field": "my_field", <- Mandatory
#       "pattern": 10, <- Mandatory
#       "variable": True, <- Optional Assignment Parameter
#       "variable_name": "my_field" <- Optional Assignment Parameter
#    }
# ]
#
# ...


class regex(BaseDetector):
    def __init__(self):
        self._result = {}

    def param_compute(self, source, regex_conf):
        # type: (dict, dict) -> None
        rules_needed_to_pass = len(regex_conf)
        rules_passed = 0
        final_result = {'result': False}
        for regex_param in regex_conf:
            # loop through the parameter set
            if regex_param['field'] in source:
                # Incase field is None type (Null from JSON) Transform to empty string for operations
                if source[regex_param['field']] is None:
                    source[regex_param['field']] = ''
                # if the field exists in the source record lets work with its
                result = re.findall(regex_param['pattern'], source[regex_param['field']])
                if len(result) > 0:
                    if 'variable' in regex_param:
                        if regex_param['variable'] and 'variable_name' in regex_param:
                            final_result[regex_param['variable_name']] = result
                    rules_passed += 1
                continue
            else:
                # We have no source field to parse
                self._result = {'result': False}
                return None
        if rules_passed == rules_needed_to_pass:
            final_result['result'] = True
            self._result = final_result
            return None
        else:
            self._result = {'result': False}
            return None

    def get_result(self):
        # type: () -> dict
        return self._result
