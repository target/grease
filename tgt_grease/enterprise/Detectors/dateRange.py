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
                        'format': '%Y-%m-%d', # <-- Mandatory via strptime behavior
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
        finalBool = False
        final = {}
        # type checks
        if not isinstance(source, dict):
            return False, {}
        if not isinstance(ruleConfig, list):
            return False, {}
        for block in ruleConfig:
            if not isinstance(block, dict):
                self.ioc.getLogger().error(
                    "INVALID DATERANGE LOGICAL BLOCK! NOT TYPE LIST [{0}]".format(str(type(block))),
                    notify=False
                )
                return False, {}
            # ensure field is there and date format
            if not block.get('field') in source or 'format' not in block:
                self.ioc.getLogger().error(
                    "malformed rule block; field and/or format not found in source",
                    notify=False
                )
                return False, {}
            if not source.get(block.get('field')):
                self.ioc.getLogger().error(
                    "field equated to False!",
                    notify=False
                )
                return False, {}
            if self.timeCompare(source.get(block.get('field')), block):
                finalBool = True
                if block.get('variable') and block.get('variable_name'):
                    final[str(block.get('variable_name'))] = source.get(block.get('field'))
                else:
                    continue
            else:
                self.ioc.getLogger().trace("Field Failed Range Comparison", verbose=True)
                return False, {}
        return finalBool, final

    def timeCompare(self, field, LogicalBlock):
        """Compares a date to a range

        Args:
            field (str): field to compare
            LogicalBlock (dict): Logical Block

        Returns:
            bool: if the range is successful then true else false

        """
        try:
            source_date = datetime.datetime.strptime(field, LogicalBlock.get('format'))
            # Ensure field is present
            # ensure at least min OR max is present
            if not LogicalBlock.get('min') and not LogicalBlock.get('max'):
                self.ioc.getLogger().trace("[min] and/or [max] not found in config block", verbose=True)
                return False
            if LogicalBlock.get('min') and LogicalBlock.get('max'):
                # Min & Max Defined
                if datetime.datetime.strptime(LogicalBlock.get('min'), LogicalBlock.get('format')) <= source_date <= datetime.datetime.strptime(LogicalBlock.get('max'), LogicalBlock.get('format')):
                    return True
                else:
                    return False
            elif LogicalBlock.get('min') and not LogicalBlock.get('max'):
                # Min Defined
                if source_date >= datetime.datetime.strptime(LogicalBlock.get('min'), LogicalBlock.get('format')):
                    return True
                else:
                    return False
            elif not LogicalBlock.get('min') and LogicalBlock.get('max'):
                # Max Defined
                if source_date <= datetime.datetime.strptime(LogicalBlock.get('max'), LogicalBlock.get('format')):
                    return True
                else:
                    return False
            else:
                self.ioc.getLogger().error("Failed to find either min OR max in LogicalBlock", verbose=True, notify=False)
                return False
        except ValueError:
            # probable datetime format error
            self.ioc.getLogger().error("Value error processing rule!", notify=False)
            return False
        except TypeError:
            # probable datetime format error
            self.ioc.getLogger().error("Type error processing rule!", notify=False)
            return False
