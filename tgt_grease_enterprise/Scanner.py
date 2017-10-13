import os
from tgt_grease_daemon.BaseCommand import GreaseDaemonCommand
from .Detectors import DetectorConfiguration
from tgt_grease_core_util import SQLAlchemyConnection, Configuration
from tgt_grease_core_util.ImportTools import Importer
from tgt_grease_core_util.RDBMSTypes import JobServers, SourceData
from tgt_grease_enterprise import BaseSource
from .DeDuplification import SourceDeDuplify
from datetime import datetime
from sqlalchemy import update


class ScanOnConfig(GreaseDaemonCommand):
    def __init__(self):
        super(ScanOnConfig, self).__init__()
        self._config = Configuration()
        self._sql = SQLAlchemyConnection(self._config)
        self._scanner_config = DetectorConfiguration.ConfigurationLoader()
        self._context = '{}'
        self._source_data = {}
        self._importer = Importer(self._ioc.message())
        self._duplification_filter = SourceDeDuplify(self._ioc.message())

    def __del__(self):
        super(ScanOnConfig, self).__del__()
        self._sql.get_session().close()
        self._duplification_filter.__del__()
        del self._duplification_filter

    def get_source_data(self):
        # type: () -> dict
        return self._source_data

    def set_source_data(self, data):
        # type: (dict) -> None
        self._source_data = data

    def execute(self, context='{}'):
        # engage scanning
        self.scan()
        # clear up this 
        del self._duplification_filter
        return True

    def scan(self):
        # engage scanners scotty
        for scanner in self._scanner_config.get_scanners():
            self._ioc.message().debug(
                "STARTING SCANNER [{0}]".format(str(scanner)),
                True
            )
            # Ensure if we are focused only to process our source
            if os.getenv('GREASE_SOURCE_FOCUS'):
                # we have one, ensure its on the list of configured scanners
                if str(os.getenv('GREASE_SOURCE_FOCUS')) != str(scanner):
                    # It does not match, continue
                    self._ioc.message().info(
                        "Scanner skipped because not focus: ["
                        + str(scanner)
                        + "] searching for ["
                        + str(os.getenv('GREASE_SOURCE_FOCUS'))
                        + "]"
                    )
                    continue
            # lets loop through our scanners/detectors to execute the parsing
            # try to load the scanner we want
            parser = self._importer.load(os.getenv('GREASE_SOURCES_PKG', ''), scanner, True)
            # type check that bad boy to ensure sanity
            if isinstance(parser, BaseSource):
                # if we got back a valid source lets parse that sucker
                self._ioc.message().debug(
                    "PARSING SOURCE [{0}]".format(str(scanner)),
                    True
                )
                parser.parse_source(self._scanner_config.get_scanner_config(scanner))
                # lets get the results of the parse
                # here we run our de-duplication logic
                self._ioc.message().debug(
                    "PASSING RESULT TO DEDUPLICATION ENGINE [{0}]".format(str(scanner)),
                    True
                )
                source = self._duplification_filter.create_unique_source(
                    scanner,
                    parser.duplicate_check_fields(),
                    list(parser.get_records())
                )
                self._ioc.message().debug(
                    "ATTEMPTING DETECTION SCHEDULING [{0}]".format(str(scanner)),
                    True
                )
                if self._schedule_detection(source, scanner):
                    self._ioc.message().info("Detector job scheduled from scanner: [" + str(scanner) + "]")
                else:
                    self._ioc.message().error("Failed to schedule source detection for [" + str(scanner) + "]", hipchat=True)
                del parser
            else:
                # else something went haywire pls feel free to fix your config
                self._ioc.message().error("Invalid Scanner In Configurations: [" + str(scanner) + "]", hipchat=True)

    def _schedule_detection(self, sources, scanner):
        # type: (dict, str)  -> bool
        # first lets get applicable servers to run detectors
        # lets only get the least assigned server so we can round robin
        result = self._sql.get_session()\
            .query(JobServers)\
            .filter(JobServers.detector == True)\
            .filter(JobServers.active == True)\
            .order_by(JobServers.jobs_assigned)\
            .first()
        if not result:
            self._ioc.message().error("Failed to find detection server! dropping scan!", hipchat=True)
            return False
        else:
            server = result.id
        # Now lets insert the sources for the determined server to work
        source = SourceData(
            source_data=sources,
            source_server=self._config.node_db_id(),
            detection_server=server,
            scanner=scanner,
            created_time=datetime.utcnow()
        )
        self._sql.get_session().add(source)
        self._sql.get_session().commit()
        # finally lets ensure we account for the fact our server is going to do
        # that job and increment the assignment counter
        stmt = update(JobServers).where(JobServers.id == server).values(jobs_assigned=result.jobs_assigned + 1)
        self._sql.get_session().execute(stmt)
        self._sql.get_session().commit()
        self._ioc.message().debug(
            "SOURCE SCHEDULED FOR DETECTION [{0}] TO SERVER [{1}]".format(str(scanner), str(server)),
            True
        )
        return True
