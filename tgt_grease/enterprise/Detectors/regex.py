from tgt_grease.enterprise.Model import Detector
import re


class Regex(Detector):
    """Regular Expression Detector for GREASE Detection

    A Typical Regex configuration looks like this::

        {
            ...
            'logic': {
                'Regex': [
                    {
                        'field': String, # <-- Field to search for
                        'pattern': String, # <-- Regex to perform on field
                        'variable': Boolean, # <-- OPTIONAL, if true then create a context variable of result
                        'variable_name: String # <-- REQUIRED IF variable, name of context variable
                    }
                    ...
                ]
                ...
            }
        }

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
        if not isinstance(source, dict):
            return False, {}
        if not isinstance(ruleConfig, list):
            return False, {}
        else:
            # loop through configuration for each set of logical configurations
            for block in ruleConfig:
                if not isinstance(block, dict):
                    self.ioc.getLogger().error(
                        "INVALID REGEX LOGICAL BLOCK! NOT TYPE LIST [{0}]".format(str(type(block))),
                        notify=False
                    )
                    return False, {}
                else:
                    # look for field and perform regex
                    if block.get('field') in source:
                        if source.get(block.get('field')):
                            result = re.findall(block.get('pattern'), str(source.get(block.get('field'))))
                            if len(result):
                                finalBool = True
                                if block.get('variable') and block.get('variable_name'):
                                    final[str(block.get('variable_name'))] = result
                                else:
                                    continue
                            else:
                                self.ioc.getLogger().trace(
                                    "Field did not pass regex",
                                    verbose=True
                                )
                                return False, {}
                        else:
                            # truthy false field value
                            self.ioc.getLogger().trace(
                                "Field [{0}] equates to false [{1}]".format(
                                    block.get('field'),
                                    source.get(block.get('field'))
                                ),
                                notify=False,
                                verbose=True
                            )
                            return False, {}
                    else:
                        self.ioc.getLogger().trace(
                            "Field not found in source [{0}]".format(block.get('field')),
                            notify=False,
                            verbose=True
                        )
                        return False, {}
            return finalBool, final
