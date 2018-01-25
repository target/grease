from tgt_grease.core import GreaseContainer
import pkg_resources
import os
import fnmatch
import json

GREASE_PROTOTYPE_CONFIGURATION = None


class PrototypeConfig(object):
    """Responsible for Scanning/Detection/Scheduling configuration

    Structure of Configuration::

        {
            'configuration': {
                'pkg': [], # <-- Loaded from pkg_resources.resource_filename('tgt_grease.enterprise.Model', 'config/')
                'fs': [], # <-- Loaded from `<GREASE_DIR>/etc/*.config.json`
                'mongo': [] # <-- Loaded from the Configuration Mongo Collection
            },
            'raw': [], # <-- All loaded configurations
            'sources': [], # <-- list of sources found in configurations
            'source': {} # <-- keys will be source values list of configs for that source
            'names': [], # <-- all configs via their name so to allow dialing
            'name': {} # <-- all configs via their name so to allow being dialing
        }

    Structure of a configuration file::

        {
            "name": String,
            "job": String,
            "exe_env": String, # <-- If not provided will be default as 'general'
            "source": String,
            "logic": {
                # I need to be the logical blocks for Detection
            }
        }

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
            dict: Configuration object

        """
        global GREASE_PROTOTYPE_CONFIGURATION
        if not GREASE_PROTOTYPE_CONFIGURATION:
            self.load(reloadConf=True)
        return GREASE_PROTOTYPE_CONFIGURATION

    def load(self, reloadConf=False, ConfigurationList=None):
        """[Re]loads configuration data about the current execution node

        Configuration data loads from 3 places in GREASE. The first is internal to the package, if one were to manually
        add their own files into the package in the current directory following the file pattern. The next is following
        the same pattern but loaded from `<GREASE_DIR>/etc/`. The final place GREASE looks for configuration data is
        from the `configuration` collection in MongoDB

        Args:
            reloadConf (bool): If True this will reload the global object. False will return the object
            ConfigurationList (list of dict): If provided will load the list of dict for config after validation

        Note:
            Providing a configuration *automatically* reloads the memory structure of prototype configuration

        Returns:
            dict: Current Configuration information

        """
        global GREASE_PROTOTYPE_CONFIGURATION
        if ConfigurationList:
            conf = dict()
            conf['configuration'] = dict()
            conf['configuration']['ConfigurationList'] = self.validate_config_list(ConfigurationList)
            conf['raw'] = conf['configuration']['ConfigurationList']
            # split by configuration sets
            # the list of configured sources
            conf['sources'] = list()
            # the actual configurations for each source
            conf['source'] = dict()
            # configurations to get via name
            conf['names'] = list()
            # the actual configurations for each config name
            conf['name'] = dict()
            for config in conf.get('raw'):  # type: dict
                if config.get('source') in conf['sources']:
                    conf['source'][config.get('source')].append(config)
                else:
                    conf['sources'].append(config.get('source'))
                    conf['source'][config.get('source')] = list()
                    conf['source'][config.get('source')].append(config)
                if config.get('name') in conf['names']:
                    self.ioc.getLogger().error(
                        "Prototype Configuration [{0}] already found! Overwriting".format(config.get('name'))
                    )
                    conf['name'][config.get('name')] = config
                else:
                    conf['names'].append(config.get('name'))
                    conf['name'][config.get('name')] = config
            GREASE_PROTOTYPE_CONFIGURATION = conf
            return conf
        # fill out raw results
        conf = dict()
        conf['configuration'] = dict()
        conf['raw'] = []
        pkg = self.validate_config_list(self.load_from_fs(
            pkg_resources.resource_filename('tgt_grease.enterprise.Model', 'config/')
        ))
        for newConfig in pkg:
            conf['raw'].append(newConfig)
        conf['configuration']['pkg'] = pkg
        del pkg
        fs = self.validate_config_list(self.load_from_fs(
            self.ioc.getConfig().get('Configuration', 'dir')
        ))
        for newConfig in fs:
            conf['raw'].append(newConfig)
        conf['configuration']['fs'] = fs
        del fs
        mongo = self.validate_config_list(self.load_from_mongo())
        for newConfig in mongo:
            conf['raw'].append(newConfig)
        conf['configuration']['mongo'] = mongo
        del mongo
        # split by configuration sets
        # the list of configured sources
        conf['sources'] = list()
        # the actual configurations for each source
        conf['source'] = dict()
        # configurations to get via name
        conf['names'] = list()
        # the actual configurations for each config name
        conf['name'] = dict()
        for config in conf.get('raw'):  # type: dict
            if config.get('source') in conf['sources']:
                conf['source'][config.get('source')].append(config)
            else:
                conf['sources'].append(config.get('source'))
                conf['source'][config.get('source')] = list()
                conf['source'][config.get('source')].append(config)
            if config.get('name') in conf['names']:
                self.ioc.getLogger().error(
                    "Prototype Configuration [{0}] already found! Overwriting".format(config.get('name'))
                )
                conf['name'][config.get('name')] = config
            else:
                conf['names'].append(config.get('name'))
                conf['name'][config.get('name')] = config
        # return block
        if not reloadConf:
            return conf
        else:
            GREASE_PROTOTYPE_CONFIGURATION = conf
            return conf

    def get_sources(self):
        """Returns the list of sources to be scanned

        Returns:
            list: List of sources

        """
        global GREASE_PROTOTYPE_CONFIGURATION  # type: dict
        if GREASE_PROTOTYPE_CONFIGURATION:
            return GREASE_PROTOTYPE_CONFIGURATION.get('sources', [])
        else:
            self.ioc.getLogger().error("GREASE Prototype configuration is not loaded", trace=True, notify=False)
            return []

    def get_source(self, name):
        """Get all configuration by source by name

        Args:
            name (str): Source name to get

        Returns:
            list[dict]: Configuration if found else empty dict

        """
        global GREASE_PROTOTYPE_CONFIGURATION
        if GREASE_PROTOTYPE_CONFIGURATION:
            return GREASE_PROTOTYPE_CONFIGURATION.get('source').get(name, [])
        else:
            self.ioc.getLogger().error("GREASE Prototype configuration not loaded", notify=False, trace=True)
            return []

    def get_names(self):
        """Returns the list of names of configs

        Returns:
            list: List of config names

        """
        global GREASE_PROTOTYPE_CONFIGURATION  # type: dict
        if GREASE_PROTOTYPE_CONFIGURATION:
            return GREASE_PROTOTYPE_CONFIGURATION.get('names', [])
        else:
            self.ioc.getLogger().error("GREASE Prototype configuration is not loaded", trace=True, notify=False)
            return []

    def get_config(self, name):
        """Get Configuration by name

        Args:
            name (str): Configuration name to get

        Returns:
            dict: Configuration if found else empty dict

        """
        global GREASE_PROTOTYPE_CONFIGURATION
        if GREASE_PROTOTYPE_CONFIGURATION:
            if GREASE_PROTOTYPE_CONFIGURATION.get('name'):
                return GREASE_PROTOTYPE_CONFIGURATION.get('name').get(name, {})
            else:
                self.ioc.getLogger().error("GREASE Configuration Not Found", notify=False, trace=True)
                return {}
        else:
            self.ioc.getLogger().error("GREASE Prototype configuration not loaded", notify=False, trace=True)
            return {}

    def load_from_fs(self, directory):
        """Loads configurations from provided directory

        Note:
            Pattern is `*.config.json`

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
        for doc in matches:
            self.ioc.getLogger().trace("Attempting to load [{0}]".format(doc), trace=True)
            with open(doc, 'rb') as current_file:
                content = current_file.read()
                if isinstance(content, bytes):
                    content = content.decode()
            try:
                intermediate.append(json.loads(content))
                self.ioc.getLogger().trace("Successfully loaded [{0}]".format(doc), trace=True)
            except ValueError:
                self.ioc.getLogger().error("Failed to load [{0}]".format(doc), trace=True, notify=False)
                continue
        self.ioc.getLogger().trace("total documents returned from fs [{0}]".format(len(intermediate)), trace=True)
        return intermediate

    def load_from_mongo(self):
        """Returns all active configurations from the mongo collection Configuration

        Structure of Configuration expected in Mongo::

            {
                "name": String,
                "job": String,
                "exe_env": String, # <-- If not provided will be default as 'general'
                "active": Boolean, # <-- set to true to load configuration
                "type": "prototype_config", # <-- MUST BE THIS VALUE; For it is the config type :)
                "source": String,
                "logic": {
                    # I need to be the logical blocks for Detection
                }
            }

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
                "exe_env": String, # <-- If not provided will be default as 'general'
                "source": String,
                "logic": {
                    # I need to be the logical blocks for Detection
                }
            }

        Args:
            config (dict): Configuration to validate

        Returns:
            bool: If it is a valid configuration

        """
        self.ioc.getLogger().trace("Configuration to be validated: [{0}]".format(config), trace=True)
        if not isinstance(config, dict):
            self.ioc.getLogger().error(
                "Configuration Validation Failed! Not of Type Dict::Got [{0}]".format(str(type(config))),
                trace=True,
                notify=False
            )
        if config.get('name'):
            if not isinstance(config.get('name'), str):
                config['name'] = str(config.get('name'))
        else:
            self.ioc.getLogger().error("Configuration does not have valid name field", trace=True, notify=False)
            return False
        if config.get('job'):
            if not isinstance(config.get('job'), str):
                config['job'] = str(config.get('job'))
        else:
            self.ioc.getLogger().error("Configuration does not have valid job field", trace=True, notify=False)
            return False
        if config.get('source'):
            if not isinstance(config.get('source'), str):
                config['source'] = str(config.get('source'))
        else:
            self.ioc.getLogger().error("Configuration does not have valid source field", trace=True, notify=False)
            return False
        if not isinstance(config.get('logic'), dict):
            self.ioc.getLogger().error("Configuration does not have valid logic field", trace=True, notify=False)
            return False
        if not config.get('logic'):
            # empty dictionary check AKA no logical blocks
            return False
        for key, params in config.get('logic').items():
            if not isinstance(params, list):
                self.ioc.getLogger().error("Configuration logic field was not list!", trace=True, notify=False)
                return False
            for block in params:
                if not isinstance(block, dict):
                    self.ioc.getLogger().error("Configuration logical block was not dict", trace=True, notify=False)
                    return False
        return True
