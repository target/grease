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
        Configuration = self.generate_config_set(source=source, config=config)
        ScanPool = []
        lenConfigs = len(Configuration)
        i = 0
        while i < lenConfigs:
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
            conf = Configuration[i]
            i += 1
            # ensure no kafka prototypes come into sourcing
            if conf.get('source') == 'kafka':
                continue
            # ensure there is an execution environment
            server, _ = self.scheduler.determineExecutionServer(conf.get('exe_env', 'general'))
            if not server:
                self.ioc.getLogger().warning(
                    'configuration skipped -- execution environment offline',
                    additional={
                        'execution_environment': conf.get('exe_env', 'general'),
                        'configuration': conf.get('name')
                    },
                    notify=True
                )
                continue
            inst = self.impTool.load(conf.get('source', str(uuid4())))
            if not isinstance(inst, BaseSourceClass):
                self.ioc.getLogger().error("Invalid Source [{0}]".format(conf.get('source')), notify=False)
                del inst
                continue
            else:
                t = threading.Thread(
                    target=self.ParseSource,
                    args=(
                        self.ioc,
                        inst,
                        conf,
                        self.dedup,
                        self.scheduler,
                    ),
                    name="GREASE SOURCING THREAD [{0}]".format(conf.get('name'))
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
    def ParseSource(ioc, source, configuration, deduplication, scheduler):
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
                data = source.mock_data(configuration)
            # else actually do sourcing
            else:
                if source.parse_source(configuration):
                    # deduplicate data
                    data = deduplication.Deduplicate(
                        data=source.get_data(),
                        source=configuration.get('source'),
                        configuration=configuration.get('name', str(uuid4())),
                        threshold=source.deduplication_strength,
                        expiry_hours=source.deduplication_expiry,
                        expiry_max=source.deduplication_expiry_max,
                        collection='Dedup_Sourcing',
                        field_set=source.field_set
                    )
                else:
                    ioc.getLogger().warning(
                        "Source [{0}] parsing failed".format(configuration.get('source')),
                        notify=False
                    )
                    data = []
            if len(data) > 0:
                if scheduler.scheduleDetection(configuration.get('source'), configuration.get('name'), data):
                    ioc.getLogger().info(
                        "Data scheduled for detection from source [{0}]".format(configuration.get('source')),
                        trace=True
                    )
                    del source
                else:
                    ioc.getLogger().error("Scheduling failed for source document!", notify=False)
                    del source
            else:
                ioc.getLogger().trace("Length of data was empty; was not scheduled", trace=True)
                del source
        except BaseException as e:
            ioc.getLogger().error(
                "Failed parsing message got exception! Configuration [{0}] Got [{1}]".format(configuration, e)
            )
            del source

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
