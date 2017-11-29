from tgt_grease.enterprise.Model import Detector
import datetime


class DateDelta(Detector):
    """Date Delta Detector for GREASE Detection

    This detector differs from DateRange as it is relative. In DateRange you can determine constant days whereas
    DateDelta can tell you how many days in the future or past a field is from the date either specified or the
    current date.

    A Typical DateDelta configuration looks like this::

        {
            ...
            'logic': {
                'DateDelta': [
                    {
                        'field': String, # <-- Field to search for
                        'delta': String, # <-- timedelta key for delta range; Accepted Values: weeks, days, hours, minutes, seconds, milliseconds, microseconds,
                        'delta_value': Int, # <-- numeric value for delta to be EX: 1 weeks
                        'format': '%Y-%m-%d', # <-- Mandatory via strptime behavior
                        'operator': String, # <-- Accepted Values: < <= > >= = !=
                        'direction': String, # <-- Accepted Values: future past
                        'date': String, # <-- OPTIONAL, if set then operation will be performed on this date compared to field
                        'variable': Boolean, # <-- OPTIONAL, if true then create a context variable of result
                        'variable_name: String # <-- REQUIRED IF variable, name of context variable
                    }
                    ...
                ]
                ...
            }
        }

    Note:
        Change the format to any supported https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
    Note:
        If date field not provided will be assumed to be UTC Time

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
            if not block.get('field') in source \
                    or 'format' not in block \
                    or not block.get('delta') \
                    or not block.get('operator') \
                    or not block.get('direction') \
                    or block.get('delta') not in ['weeks', 'days', 'hours', 'minutes', 'seconds', 'milliseconds', 'microseconds'] \
                    or not block.get('delta_value'):
                self.ioc.getLogger().error(
                    "malformed rule block; fields [delta, operator, format] are required but not found"
                    " or field not found in source",
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
        """Compares a date to find a delta

        Args:
            field (str): field to compare
            LogicalBlock (dict): Logical Block

        Returns:
            bool: if the range is successful then true else false

        """
        try:
            source_date = datetime.datetime.strptime(field, LogicalBlock.get('format'))
            if LogicalBlock.get('direction') is 'future':
                direction = 1
            elif LogicalBlock.get('direction') is 'past':
                direction = -1
            else:
                self.ioc.getLogger().error("key [direction] is not future or past", notify=False)
                return False
            # setup compare object
            if LogicalBlock.get('date'):
                compare_date = datetime.datetime.strptime(LogicalBlock.get('date'), LogicalBlock.get('format')) \
                               + datetime.timedelta(**{
                                    str(LogicalBlock.get('delta')): int(LogicalBlock.get('delta_value'))
                               }) \
                               * direction
            else:
                compare_date = datetime.datetime.utcnow().strftime(LogicalBlock.get('format'))
                compare_date = datetime.datetime.strptime(compare_date, LogicalBlock.get('format')) \
                               + datetime.timedelta(**{
                                    str(LogicalBlock.get('delta')): int(LogicalBlock.get('delta_value'))
                               }) \
                               * direction
            if LogicalBlock.get('operator') == '<':
                ReturnBool = (source_date < compare_date)
            elif LogicalBlock.get('operator') == '<=':
                ReturnBool = (source_date <= compare_date)
            elif LogicalBlock.get('operator') == '>':
                ReturnBool = (source_date > compare_date)
            elif LogicalBlock.get('operator') == '>=':
                ReturnBool = (source_date >= compare_date)
            elif LogicalBlock.get('operator') == '=':
                ReturnBool = (source_date == compare_date)
            elif LogicalBlock.get('operator') == '!=':
                ReturnBool = (source_date != compare_date)
            else:
                self.ioc.getLogger().error(
                    "Invalid operator provided [{0}]".format(LogicalBlock.get('operator')),
                    notify=False
                )
                return False
            return ReturnBool
        except ValueError:
            # probable datetime format error
            self.ioc.getLogger().error("Value error processing rule!", notify=False)
            return False
        except TypeError:
            # probable datetime format error
            self.ioc.getLogger().error("Type error processing rule!", notify=False)
            return False
