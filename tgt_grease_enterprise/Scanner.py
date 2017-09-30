import json
import os
from tgt_grease_daemon.BaseCommand import GreaseDaemonCommand
from .Detectors import DetectorConfiguration
from tgt_grease_core_util import Database
from tgt_grease_core_util.ImportTools import Importer
from tgt_grease_enterprise import BaseSource
from .DeDuplification import SourceDeDuplify


class ScanOnConfig(GreaseDaemonCommand):
    def __init__(self):
        super(ScanOnConfig, self).__init__()
        self._conn = Database.Connection()
        self._scanner_config = DetectorConfiguration.ConfigurationLoader()
        self._context = '{}'
        self._source_data = {}
        self._importer = Importer(self._ioc.message())
        self._duplification_filter = SourceDeDuplify(self._ioc.message())

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
                    self._ioc.message().error("Failed to schedule source detection for [" + str(scanner) + "]")
                del parser
            else:
                # else something went haywire pls feel free to fix your config
                self._ioc.message().error("Invalid Scanner In Configurations: [" + str(scanner) + "]")

    def _schedule_detection(self, sources, scanner):
        # type: (dict, str)  -> bool
        # first lets get applicable servers to run detectors
        # lets only get the least assigned server so we can round robin
        sql = """
            SELECT
              js.id,
              js.jobs_assigned
            FROM
              grease.job_servers js
            WHERE
              js.detector = TRUE AND 
              js.active is true
            ORDER BY 
              js.jobs_assigned
            LIMIT 1
        """
        server = self._conn.query(sql)
        if len(server) <= 0:
            self._ioc.message().error("Failed to get server to schedule sources for!::Dropping Scan")
            return False
        else:
            server = server[0]
        # Now lets insert the sources for the determined server to work
        sql = """
            INSERT INTO
              grease.source_file
            (source_document, job_server, scanner) 
            VALUES 
            (
              %s,
              %s,
              %s
            )
        """
        self._conn.execute(sql, (json.dumps(sources), server[0], scanner,))
        # finally lets ensure we account for the fact our server is going to do
        # that job and increment the assignment counter
        sql = """
            UPDATE
              grease.job_servers
            SET
              jobs_assigned = %s
            WHERE
              id = %s
        """
        self._ioc.message().debug(
            "SOURCE SCHEDULED FOR DETECTION [{0}] TO SERVER [{1}]".format(str(scanner), str(server[0])),
            True
        )
        self._conn.execute(sql, (int(server[1]) + 1, server[0],))
        return True
