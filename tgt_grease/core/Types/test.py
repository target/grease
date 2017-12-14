from unittest import TestCase
from unittest.case import SkipTest
from tgt_grease.core import GreaseContainer
from tgt_grease.enterprise.Model import Detect
import pkg_resources
import os
import json


class AutomationTest(TestCase):
    """Automation Test Class

    Version II of GREASE was all about proving stability. Automation testing is critically important to ensure
    reliability during fault isolation. This class is an abstract class your tests can implement to ensure they
    will perform exactly as you expect in production.

    Make sure you set the **configuration** class attribute to ensure your configuration is tested, the **mock_data**
    class attribute with your mock data dictionary you expect to be sourced in production, and the **expected_data**
    with what you expect detection to find from your mocked source data. Then implement the **test_command** method to
    write standard unittests around your automation. The Platform will test your configuration for you, and execute
    **test_command** with `python setup.py test` is executed.

    Attributes:
        configuration (str|dict): Configuration to load for this test
        mock_data (dict): String Key -> Int/Float/String Value pair to mock source data
        expected_data (dict): data you expect context for your command to look like
        enabled (bool): set to true to enable your test to run

    Here is an example::

        class TestAutomationTest(AutomationTest):

            def __init__(self, *args, **kwargs):
                AutomationTest.__init__(self, *args, **kwargs)
                self.configuration = "mongo://test_automation_test"
                self.mock_data = {'ver': 'var'}
                self.expected_data = {'ver': ['var']}
                self.enabled = True

            def test_command(self):
                myCommand = myCommand()
                self.assertTrue(myCommand.execute({'hostname': 'localhost'}))

    This is a pretty basic example but it will help you get started automatically testing your automation!

    Note:
        **YOU MUST SET THE PROPERTY `ENABLED` TO BOOLEAN TRUE IN ORDER FOR YOUR TEST TO BE PICKED UP**
    Note:
        To use a static configuration set `configuration` to a dictionary
    Note:
        To use a MongoDB configuration for a test prefix your configuration's name with mongo://
    Note:
        To use a package configuration for a test prefix your configuration's name with pkg://
    Note:
        to use a filesystem configuration for a test prefix your configuration's path with fs://

    """

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        self.configuration = None
        self.enabled = False
        self.mock_data = {}
        self.expected_data = {}
        self.ioc = GreaseContainer()
        self.detect = Detect(self.ioc)

    def test_configuration(self):
        """Configuration Test

        This method tests your configuration and validates that detection will return as you expect

        """
        if not self.enabled:
            raise SkipTest
        self.assertTrue(self.configuration, "Ensure configuration is not empty")
        self.assertIsInstance(self.configuration, str, "Ensure configuration is type string")
        self.assertTrue(self.mock_data, "Ensure mock_data is not empty")
        self.assertIsInstance(self.mock_data, dict, "Ensure mock_data is type dict")
        self.assertTrue(self.expected_data, "Ensure expected_data is not empty")
        self.assertIsInstance(self.expected_data, dict, "Ensure expected_data is type dict")
        config = None
        if str(self.configuration).startswith("mongo://"):
            config = self.ioc.getCollection('Configuration').find_one({
                'name': str(self.configuration).split("://")[1],
                'active': True,
                "type": "prototype_config"
            })
            self.assertTrue(config, "Ensuring MongoDB has configuration")
            config = dict(config)
        elif str(self.configuration).startswith("pkg://"):
            if os.path.isfile(pkg_resources.resource_filename('tgt_grease', str(self.configuration).split("://")[1])):
                with open(pkg_resources.resource_filename('tgt_grease', str(self.configuration).split("://")[1]), 'rb') as fil:
                    config = json.loads(fil.read())
                    self.assertIsInstance(config, dict, "Ensuring Valid JSON")
            else:
                self.assertTrue(
                    False,
                    "Failed to load [{0}] from tgt_grease pkg".format(str(self.configuration).split("://")[1])
                )
        elif str(self.configuration).startswith("fs://"):
            if os.path.isfile(str(self.configuration).split("://")[1]):
                with open(str(self.configuration).split("://")[1], 'rb') as fil:
                    config = json.loads(fil.read())
                    self.assertIsInstance(config, dict, "Ensuring Valid JSON")
            else:
                self.assertTrue(
                    False,
                    "Failed to load [{0}] from filesystem".format(str(self.configuration).split("://")[1])
                )
        else:
            self.assertTrue(False, "Failed to load configuration::Invalid Configuration Location Type")
        self.assertTrue(config, "Ensuring config is not boolean equatable to False")
        result, context = self.detect.detection(self.mock_data, config)
        self.assertTrue(result, "Detection Results")
        self.assertDictEqual(context, self.expected_data, "validating context expected")

    def test_command(self):
        """This method is for **you** to fill out to test your command

        Note:
            The more tests the better! Make sure to add as many tests as you need to ensure your automation is always successful

        """
        if not self.enabled:
            raise SkipTest
