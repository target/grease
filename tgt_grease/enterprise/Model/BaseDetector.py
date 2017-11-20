from abc import ABCMeta, abstractmethod
from tgt_grease.core import GreaseContainer


class Detector(object):
    """Base Detection Class

    This is the abstract class for detectors to implement

    Attributes:
        ioc (GreaseContainer): IOC Access

    """

    __metaclass__ = ABCMeta

    def __init__(self, ioc=None):
        if isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()

    @abstractmethod
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
