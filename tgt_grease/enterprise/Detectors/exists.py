from tgt_grease.enterprise.Model import Detector


class Exists(Detector):
    """Field Existence Detector for GREASE Detection

    A Typical Regex configuration looks like this::

        {
            ...
            'logic': {
                'Exists': [
                    {
                        'field': String, # <-- Field to search for
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
        # type checks
        if not isinstance(source, dict):
            return False, {}
        if not isinstance(ruleConfig, list):
            return False, {}
        else:
            # loop through configuration for each set of logical configurations
            for block in ruleConfig:
                if not isinstance(block, dict):
                    self.ioc.getLogger().error(
                        "INVALID EXISTS LOGICAL BLOCK! NOT TYPE LIST [{0}]".format(str(type(block))),
                        notify=False
                    )
                    return False, {}
                else:
                    # look for field and perform exists check
                    if block.get('field') in source:
                        if source.get(block.get('field')):
                            finalBool = True
                            if block.get('variable') and block.get('variable_name'):
                                final[str(block.get('variable_name'))] = source.get(block.get('field'))
                            else:
                                continue
                        else:
                            # truthy false field value
                            self.ioc.getLogger().trace(
                                "Field [{0}] equated to false [{1}]".format(
                                    block.get('field'),
                                    source.get(block.get('field'))
                                ),
                                verbose=True
                            )
                            return False, {}
                    else:
                        self.ioc.getLogger().trace(
                            "Field not found in source [{0}]".format(block.get('field')),
                            verbose=True
                        )
                        return False, {}
            return finalBool, final
