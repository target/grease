from tgt_grease.core import GreaseContainer
from tgt_grease.core import ImportTool
from .Configuration import PrototypeConfig
from .BaseSource import BaseSourceClass
from .DeDuplication import Deduplication
from .CentralScheduling import Scheduling
import threading
from psutil import cpu_percent, virtual_memory
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
        sources = self.conf.get_sources() if not source else [source]
        ScanPool = []
        for src in sources:
            # ensure no kafka prototypes come into sourcing
            if src == 'kafka':
                continue

            inst = self.impTool.load(src)
            if not isinstance(inst, BaseSourceClass):
                self.ioc.getLogger().error("Invalid Source [{0}]".format(source), notify=False)
                del inst
                continue
            else:
                # If the source wants us to bundle, do it
                bundled = self.bundle_configs(src, self.generate_config_set(source=source, config=config))
                for sentinel_conf in bundled:
                    # ensure we don't swamp the system resources
                    cpu = cpu_percent(interval=.1)
                    mem = virtual_memory().percent
                    if \
                            cpu >= int(self.ioc.getConfig().get('NodeInformation', 'ResourceMax')) or \
                            mem >= int(self.ioc.getConfig().get('NodeInformation', 'ResourceMax')):
                        self.ioc.getLogger().trace("Scan sleeping; System resource maximum reached", verbose=True)
                        # remove variables
                        del cpu
                        del mem
                        continue
                    # # ensure there is an execution environment
                    # server, _ = self.scheduler.determineExecutionServer(sentinel_conf.get('exe_env', 'general'))
                    # if not server:
                    #     self.ioc.getLogger().warning(
                    #         'configuration skipped -- execution environment offline',
                    #         additional={
                    #             'execution_environment': sentinel_conf.get('exe_env', 'general'),
                    #             'configuration': sentinel_conf.get('name')
                    #         },
                    #         notify=True
                    #     )
                    #     continue

                    t = threading.Thread(
                        target=self.ParseSource,
                        args=(
                            self.ioc,
                            inst,
                            sentinel_conf,
                            bundled.get(sentinel_conf, []),
                            self.dedup,
                            self.scheduler,
                        ),
                        name="GREASE SOURCING THREAD [{0}]".format(sentinel_conf.get('name'))
                    )
                    t.daemon = True
                    t.start()
                    ScanPool.append(t)
        # wait for threads to finish out
        while len(ScanPool) > 0:
            self.ioc.getLogger().trace("Total current scan threads [{0}]".format(len(ScanPool)), trace=True)
            threads_final = []
            for thread in ScanPool:
                if thread.isAlive():
                    threads_final.append(thread)
            ScanPool = threads_final
            self.ioc.getLogger().trace("Total current scan threads [{0}]".format(len(ScanPool)), trace=True)
        self.ioc.getLogger().trace("Scanning Complete".format(len(ScanPool)), trace=True)
        return True

    @staticmethod
    def ParseSource(ioc, source, sentinel_config, other_configs, deduplication, scheduler):
        """Parses an individual source and attempts to schedule it

        Args:
            ioc (GreaseContainer): IoC Instance
            source (BaseSourceClass): Source to parse
            configuration (dict): Prototype configuration to use
            deduplication (Deduplication): Dedup engine instance
            scheduler (Scheduling): Central Scheduling instance

        Returns:
            None: Meant to be run in a thread

        """
        try:
            # If mock mode enabled
            if ioc.getConfig().get('Sourcing', 'mock'):
                data = source.mock_data(sentinel_config)
            # else actually do sourcing
            else:
                if source.parse_source(sentinel_config):
                    # deduplicate data
                    # TODO: Dedup the rest
                    data = deduplication.Deduplicate(
                        data=source.get_data(),
                        source=sentinel_config.get('source'),
                        configuration=sentinel_config.get('name', str(uuid4())),
                        threshold=source.deduplication_strength,
                        expiry_hours=source.deduplication_expiry,
                        expiry_max=source.deduplication_expiry_max,
                        collection='Dedup_Sourcing',
                        field_set=source.field_set
                    )
                else:
                    ioc.getLogger().warning(
                        "Source [{0}] parsing failed".format(sentinel_config.get('source')),
                        notify=False
                    )
                    data = []
            if len(data) > 0:
                confs = other_configs.append(sentinel_config)
                for conf in confs:
                    if scheduler.scheduleDetection(conf.get('source'), conf.get('name'), data):
                        ioc.getLogger().info(
                            "Data scheduled for detection from source [{0}] with sentinel config [{1}]".format(
                                conf.get('source'),
                                sentinel_config
                            ),
                            trace=True
                        )
                    else:
                        ioc.getLogger().error("Scheduling failed for source document!", notify=False)
            else:
                ioc.getLogger().trace("Length of data was empty; was not scheduled", trace=True)
        except BaseException as e:
            ioc.getLogger().error(
                "Failed parsing message got exception! Configuration [{0}] Got [{1}]".format(sentinel_config, e)
            )

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

    def bundle_configs(self, source, conf_list):
        """
        Return a data structure that pairs a list with a sentinel config that represents the associated list.
        The data that is returned by the source will be valid for each config in the list. This prevents us
        from having to source many times for the same data.
        {
          "sentinel_config": ["config2", "config3", "config4"],
          ...
        }
        """
        parsed_values = {}
        bundle = {}

        # Group configs by the value of the group_by keys
        for key in source.group_by:
            confs = [x for x in conf_list if x.get(key)]
            # TODO: Handle configs that don't have any associated keys?
            for conf in confs:
                # If the value is a list, treat it as a tuple for hashing purposes in the dict
                value = conf.get(key) if type(conf.get(key)) is not list else tuple(conf.get(key))
                if value not in parsed_values:
                    parsed_values[value] = [conf.get("name")]
                else:
                    parsed_values[value].append(conf.get("name"))

        # Build the final data structure
        for value in parsed_values:
            sentinel_config = parsed_values[value][0]
            bundle[sentinel_config] = parsed_values[value][1:]

        # If we don't have a bundle, return all configs as sentinel configs
        if not bundle:
            bundle = {conf: [] for conf in conf_list}

        return bundle





