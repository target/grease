from tgt_grease.enterprise.Model import Detector
import datetime


class DateRange(Detector):
    """Date Range Detector for GREASE Detection

    A Typical DateRange configuration looks like this::

        {
            ...
            'logic': {
                'DateRange': [
                    {
                        'field': String, # <-- Field to search for
                        'min': DateTime String, # <-- OPTIONAL IF max is set
                        'max': DateTime String, # <-- OPTIONAL IF min is set
                        'date_format': '%Y-%m-%d', # <-- Mandatory via strptime behavior
                        'variable': Boolean, # <-- OPTIONAL, if true then create a context variable of result
                        'variable_name: String # <-- REQUIRED IF variable, name of context variable
                    }
                    ...
                ]
                ...
            }
        }

    Note:
        The min field is only required if max is not present. This would ensure the field is after the date provided
    Note:
        The max field is only required if min is not present. This would ensure the field is before the date provided
    Note:
        Change the format to any supported https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
    Note:
        To find an exact date/time set min one below the target and max one above the target

    """

    def processObject(self, source, ruleConfig):
        """Processes an object and returns valid rule data

        Data returned in the second parameter from this method should be in this form::

            {
                '<field>': Object # <-- if specified as a variable then return the key->Value pairs
                ...
            }

        Args:
            source (dict): Source Data
            ruleConfig (list[dict]): Rule Configuration Data

        Return:
            tuple: first element boolean for success; second dict for any fields returned as variables

        """
        pass
