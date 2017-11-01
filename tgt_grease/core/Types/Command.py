from abc import ABCMeta, abstractmethod


class Command(object):
    """Abstract class for commands in GREASE

    Attributes:
        __metaclass__ (ABCMeta): Metadata class object
        purpose (str): The purpose of the command

    """

    __metaclass__ = ABCMeta
    purpose = "Stuff"
