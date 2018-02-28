from tgt_grease.core import GreaseContainer
from tgt_grease.core import ImportTool
from .Configuration import PrototypeConfig
from .BaseSource import BaseSourceClass
from .DeDuplication import Deduplication
from .CentralScheduling import Scheduling
from uuid import uuid4


class Scan(object):
    """Scanning class for GREASE Scanner

    This is the model to actually utilize the scanners to parse the configured environments

    Attributes:
        ioc (GreaseContainer): IOC for scanning
        conf (PrototypeConfig): Prototype configuration instance
        impTool (ImportTool): Import Utility Instance
        dedup (Deduplication): Deduplication instance to be used

    """

    def __init__(self, ioc=None):
        if ioc and isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()
        self.conf = PrototypeConfig(self.ioc)
        self.impTool = ImportTool(self.ioc.getLogger())
        self.dedup = Deduplication(self.ioc)
        self.scheduler = Scheduling(self.ioc)

    def Parse(self, source=None, config=None):
        """This will read all configurations and attempt to scan the environment

        This is the primary business logic for scanning in GREASE. This method will use configurations to parse
        the environment and attempt to schedule

        Note:
            If a Source is specified then *only* that source is parsed. If a configuration is set then *only* that
            configuration is parsed. If both are provided then the configuration will *only* be parsed if it is of
            the source provided

        Note:
            **If mocking is enabled**: Deduplication *will not occur*

        Args:
            source (str): If set will only parse for the source listed
            config (str): If set will only parse the specified config

        Returns:
            bool: True unless error

        """
        self.ioc.getLogger().trace("Starting Parse of Environment", trace=True)
        Configuration = self.generate_config_set(source=source, config=config)
        for conf in Configuration:
            if conf.get('source') == 'kafka':
                continue
            inst = self.impTool.load(conf.get('source', str(uuid4())))
            if not isinstance(inst, BaseSourceClass):
                self.ioc.getLogger().error("Invalid Source [{0}]".format(conf.get('source')), notify=False)
                del inst
                continue
            else:
                # If mock mode enabled
                if self.ioc.getConfig().get('Sourcing', 'mock'):
                    data = inst.mock_data(conf)
                # else actually do sourcing
                else:
                    if inst.parse_source(conf):
                        # deduplicate data
                        data = self.dedup.Deduplicate(
                            data=inst.get_data(),
                            source=conf.get('source'),
                            configuration=conf.get('name', str(uuid4())),
                            threshold=inst.deduplication_strength,
                            expiry_hours=inst.deduplication_expiry,
                            expiry_max=inst.deduplication_expiry_max,
                            collection='Dedup_Sourcing',
                            field_set=inst.field_set
                        )
                    else:
                        self.ioc.getLogger().warning(
                            "Source [{0}] parsing failed".format(conf.get('source')),
                            notify=False
                        )
                        data = []
                if len(data) > 0:
                    if self.scheduler.scheduleDetection(conf.get('source'), conf.get('name'), data):
                        self.ioc.getLogger().info(
                            "Data scheduled for detection from source [{0}]".format(conf.get('source')),
                            trace=True
                        )
                        del inst
                        continue
                    else:
                        self.ioc.getLogger().error("Scheduling failed for source document!", notify=False)
                        del inst
                        continue
                else:
                    self.ioc.getLogger().trace("Length of data was empty; was not scheduled", trace=True)
                    del inst
                    continue
        return True

    def generate_config_set(self, source=None, config=None):
        """Examines configuration and returns list of configs to parse

        Note:
            If a Source is specified then *only* that source is parsed. If a configuration is set then *only* that
            configuration is parsed. If both are provided then the configuration will *only* be parsed if it is of
            the source provided

        Args:
            source (str): If set will only parse for the source listed
            config (str): If set will only parse the specified config

        Returns:
            list[dict]: Returns Configurations to Parse for data

        """
        ConfigList = []
        if source and config:
            if self.conf.get_config(config).get('source') == source:
                ConfigList.append(self.conf.get_config(config))
                return ConfigList
            else:
                self.ioc.getLogger().warning(
                    "Configuration [{0}] Not Found With Correct Source [{1}]".format(config, source),
                    trace=True,
                    notify=False
                )
        elif source and not config:
            if source in self.conf.get_sources():
                for configuration in self.conf.get_source(source):
                    ConfigList.append(configuration)
                return ConfigList
            else:
                self.ioc.getLogger().warning(
                    "Source not found in Configuration [{0}]".format(source),
                    trace=True,
                    notify=False
                )
        elif not source and config:
            if self.conf.get_config(config):
                ConfigList.append(self.conf.get_config(config))
                return ConfigList
            else:
                self.ioc.getLogger().warning(
                    "Config not found in Configuration [{0}]".format(config),
                    trace=True,
                    notify=False
                )
        else:
            ConfigList = self.conf.getConfiguration().get('raw')
        return ConfigList
