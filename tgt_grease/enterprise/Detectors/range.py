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
    Note:
        To find an exact number set min one below the target and max one above the target

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
                        "INVALID RANGE LOGICAL BLOCK! NOT TYPE LIST [{0}]".format(str(type(block))),
                        notify=False
                    )
                    return False, {}
                else:
                    # look for field and perform range check
                    if block.get('field') in source:
                        # perform range operation since field exists
                        if source.get(block.get('field')):
                            if self.range_compare(source.get(block.get('field')), block):
                                finalBool = True
                                if block.get('variable') and block.get('variable_name'):
                                    final[str(block.get('variable_name'))] = source.get(block.get('field'))
                                else:
                                    continue
                            else:
                                self.ioc.getLogger().trace("Field Failed Range Comparison", verbose=True)
                                return False, {}
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

    def range_compare(self, field, LogicalBlock):
        """Compares number range to a field

        Args:
            field (int/float/long): field to compare
            LogicalBlock (dict): Logical Block

        Returns:
            bool: if the range is successful then true else false

        """
        # Ensure field is present
        # ensure at least min OR max is present
        if not LogicalBlock.get('min') and not LogicalBlock.get('max'):
            self.ioc.getLogger().trace("[min] and/or [max] not found in config block", verbose=True)
            return False
        if LogicalBlock.get('min') and not isinstance(LogicalBlock.get('min'), (int, float)):
            self.ioc.getLogger().trace("min not of type int or float", verbose=True)
            return False
        if LogicalBlock.get('max') and not isinstance(LogicalBlock.get('max'), (int, float)):
            self.ioc.getLogger().trace("max not of type int or float", verbose=True)
            return False
        # ensure field is an number
        if not isinstance(field, (int, float)):
            self.ioc.getLogger().trace("Field is NaN", verbose=True)
            return False
        if LogicalBlock.get('min') and LogicalBlock.get('max'):
            # Min & Max Defined
            if isinstance(field, int):
                minValue = int(LogicalBlock.get('min'))
                maxValue = int(LogicalBlock.get('max'))
                field = int(field)
            elif isinstance(field, float):
                minValue = float(LogicalBlock.get('min'))
                maxValue = float(LogicalBlock.get('max'))
                field = float(field)
            else:
                self.ioc.getLogger().error("Internal Casting Error; Failed to determine field type", notify=False)
                return False
            if minValue <= field <= maxValue:
                return True
            else:
                return False
        elif LogicalBlock.get('min') and not LogicalBlock.get('max'):
            # Min Defined
            if isinstance(field, int):
                minValue = int(LogicalBlock.get('min'))
                field = int(field)
            elif isinstance(field, float):
                minValue = float(LogicalBlock.get('min'))
                field = float(field)
            else:
                self.ioc.getLogger().error("Internal Casting Error; Failed to determine field type", notify=False)
                return False
            if field >= minValue:
                return True
            else:
                return False
        elif not LogicalBlock.get('min') and LogicalBlock.get('max'):
            # Max Defined
            if isinstance(field, int):
                maxValue = int(LogicalBlock.get('max'))
                field = int(field)
            elif isinstance(field, float):
                maxValue = float(LogicalBlock.get('max'))
                field = float(field)
            else:
                self.ioc.getLogger().error("Internal Casting Error; Failed to determine field type", notify=False)
                return False
            if field <= maxValue:
                return True
            else:
                return False
        else:
            self.ioc.getLogger().error("Failed to find either min OR max in LogicalBlock", verbose=True, notify=False)
            return False
