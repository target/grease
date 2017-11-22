from tgt_grease.enterprise.Model import Detector


class Range(Detector):
    """Field Number Range Detector for GREASE Detection

    A Typical Range configuration looks like this::

        {
            ...
            'logic': {
                'Range': [
                    {
                        'field': String, # <-- Field to search for
                        'min': Int/float, # <-- OPTIONAL IF max is set
                        'max': Int/Float # <-- OPTIONAL IF min is set
                    }
                    ...
                ]
                ...
            }
        }

    Note:
        The min field is only required if max is not present. This would ensure the field is above the number provided
    Note:
        The max field is only required if min is not present. This would ensure the field is below the number provided
    Note:
        If both are provided then the field would need to be inside the range provided

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
        final = {}
        finalBool = False
        # type checks
        if not isinstance(source, dict):
            return False, {}
        if not isinstance(ruleConfig, list):
            return False, {}
        else:

            return finalBool, final
