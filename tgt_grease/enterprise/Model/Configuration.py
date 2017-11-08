from tgt_grease.core import GreaseContainer
import pkg_resources
import os
import fnmatch
import json

GREASE_PROTOTYPE_CONFIGURATION = None


class PrototypeConfig(object):
    """Responsible for Scanning/Detection/Scheduling configuration

    Attributes:
        ioc (GreaseContainer): IOC access

    """

    def __init__(self, ioc=None):
        global GREASE_PROTOTYPE_CONFIGURATION
        if ioc and isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()
        if not GREASE_PROTOTYPE_CONFIGURATION:
            GREASE_PROTOTYPE_CONFIGURATION = self.load()

    def getConfiguration(self):
        """Returns the Configuration Object loaded into memory

        Returns:
            list of dict: Configuration object

        """
        global GREASE_PROTOTYPE_CONFIGURATION
        if not GREASE_PROTOTYPE_CONFIGURATION:
            self.load(reloadConf=True)
        return GREASE_PROTOTYPE_CONFIGURATION

    def load(self, reloadConf=False):
        """[Re]loads configuration data about the current execution node

        Configuration data loads from 3 places in GREASE. The first is internal to the package, if one were to manually
        add their own files into the package in the current directory following the file pattern. The next is following
        the same pattern but loaded from `<GREASE_DIR>/etc/`. The final place GREASE looks for configuration data is
        from the `configuration` collection in MongoDB

        Args:
            reloadConf (bool): If True this will reload the global object. False will return the object

        Returns:
            dict: Current Configuration information

        """
        # fill out raw results
        conf = dict()
        conf['configuration'] = dict()
        conf['raw'] = []
        pkg = self.validate_config_list(self.load_from_fs(
            pkg_resources.resource_filename('tgt_grease.enterprise.Model', 'config/')
        ))
        conf['raw'].append(pkg)
        conf['configuration']['pkg'] = pkg
        del pkg
        fs = self.validate_config_list(self.load_from_fs(
            self.ioc.getConfig().get('Configuration', 'dir')
        ))
        conf['raw'].append(fs)
        conf['configuration']['fs'] = fs
        del fs
        mongo = self.validate_config_list(self.load_from_mongo())
        conf['raw'].append(mongo)
        conf['configuration']['mongo'] = mongo
        del mongo
        # split by source & detector

        # return block
        if not reloadConf:
            return conf
        else:
            global GREASE_PROTOTYPE_CONFIGURATION
            GREASE_PROTOTYPE_CONFIGURATION = conf
            return conf

    def load_from_fs(self, directory):
        """Returns all configurations from tgt_grease.enterprise.Model/config/*.config.json

        Args:
            directory (str): Directory to load from

        Returns:
            list of dict: configurations

        """
        self.ioc.getLogger().trace("Loading Configurations from directory [{0}]".format(directory), trace=True)
        intermediate = list()
        matches = []
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, '*.config.json'):
                matches.append(os.path.join(root, filename))
        result = matches
        for doc in result:
            with open(doc) as current_file:
                content = current_file.read().replace('\r\n', '')
            try:
                intermediate.append(json.loads(content))
            except ValueError:
                continue
        self.ioc.getLogger().trace("total documents returned from fs [{0}]".format(len(intermediate)), trace=True)
        return intermediate

    def load_from_mongo(self):
        """Returns all active configurations from the mongo collection Configuration

        Returns:
            list of dict: Configurations

        """
        self.ioc.getLogger().trace("Loading Configurations from mongo", trace=True)
        mConf = []
        for conf in self.ioc.getCollection('Configuration').find({
            'active': True,
            'type': 'prototype_config'
        }):
            mConf.append(dict(conf))
        self.ioc.getLogger().trace("total documents returned from mongo [{0}]".format(len(mConf)), trace=True)
        return mConf

    def validate_config_list(self, configs):
        """Validates a configuration List

        Args:
            configs (list[dict]): Configuration List

        Returns:
            list: The Valid configurations

        """
        final = []
        self.ioc.getLogger().trace("Total configurations to validate [{0}]".format(len(configs)))
        for conf in configs:
            if self.validate_config(conf):
                final.append(conf)
        return final

    def validate_config(self, config):
        """Validates a configuration

        The default JSON Schema is this::

            {
                "name": String,
                "job": String,
                "exe_env": String,
                "source": String,
                "logic": [

                ]
            }

        Args:
            config (dict): Configuration to validate

        Returns:
            bool: If it is a valid configuration

        """
        if not isinstance(config, dict):
            self.ioc.getLogger().error(
                "Configuration Validation Failed! Not of Type Dict::Got [{0}]".format(str(type(config))),
                trace=True,
                notify=False
            )
        if not config.get('job'):
            self.ioc.getLogger().error("Configuration does not have valid job field", trace=True, notify=False)
            return False
        return True
