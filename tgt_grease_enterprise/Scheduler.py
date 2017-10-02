from tgt_grease_daemon.BaseCommand import GreaseDaemonCommand
from tgt_grease_enterprise.Detectors import DetectorConfiguration
from tgt_grease_core_util import Database
from tgt_grease_core_util import SQLAlchemyConnection, Configuration
from tgt_grease_core_util.RDBMSTypes import JobServers, SourceData, JobConfig
import json
import hashlib


class Scheduler(GreaseDaemonCommand):
    def __init__(self):
        super(Scheduler, self).__init__()
        self._scanner_config = DetectorConfiguration.ConfigurationLoader()
        self._conn = Database.Connection()
        self._config = Configuration()
        self._sql = SQLAlchemyConnection(self._config)

    def execute(self, context='{}'):
        # Lets go get the jobs needing to be scheduled by this server
        result = self._sql.get_session().query(SourceData, JobServers)\
            .filter(SourceData.scheduling_server == JobServers.id)\
            .filter(JobServers.id == self._config.node_db_id())\
            .filter(SourceData.detection_start_time == None)\
            .filter(SourceData.detection_end_time == None)\
            .filter(SourceData.detection_complete == False)\
            .limit(15)\
            .all()
        if not result:
            self._ioc.message().debug("No Sources to schedule")
            return True
        else:
            for schedule in result:
                # lets own this
                self._take_ownership(schedule.SourceData.id)
                self._schedule_via_sources(schedule.SourceData.source_data)
                # lets finish out
                self._complete(schedule.SourceData.id)
        return True

    def _schedule_via_sources(self, sources):
        # type: (dict) -> None
        for index in sources:
            # check to see if we already assigned this source
            if 'grease_internal_assigned' in sources[index]:
                if sources[index]['grease_internal_assigned']:
                    # we already successfully did the thing
                    self._ioc.message().debug(
                        "SCHEDULING ALREADY PROCEEDED ON INDEX [{0}]".format(str(index)),
                        True
                    )
                    continue
                else:
                    # it failed previously
                    self._ioc.message().warning("Record Failed To Be Assigned::Loop Over")
                    continue
            else:
                # we have not attempted to schedule this record yet
                if len(sources[index]['rule_processing']) > 0:
                    # rules got processed on this source
                    for rule_name, rule_results in sources[index]['rule_processing'].iteritems():
                        self._ioc.message().debug(
                            "PROCESSING SOURCE [{0}] FOR RULE [{1}]".format(str(index), str(rule_name)),
                            True
                        )
                        if rule_results['status']:
                            self._ioc.message().debug(
                                "SOURCE [{0}] RULE [{1}] PASSED DETECTION".format(str(index), str(rule_name)),
                                True
                            )
                            # rule was successful time to schedule
                            # lets go load the rule config
                            rule_config = self._scanner_config.get_config(rule_name)
                            self._ioc.message().debug(
                                "READING CONFIG FOR RULE [{0}]".format(str(rule_name)),
                                True
                            )
                            # setup the execution environment variable
                            if 'exe_env' in rule_config:
                                if len(rule_config['exe_env']) > 0:
                                    # if we have a valid string then just set it
                                    exe_env = rule_config['exe_env']
                                else:
                                    # else they left it blank, default to general
                                    exe_env = 'general'
                            else:
                                # they didn't provide one so default to general
                                exe_env = 'general'
                            # next lets setup the SN url
                            if 'incident_url' in sources[index]:
                                # incidents URL
                                url = sources[index]['incident_url']
                                # Service Event URL
                            elif 'event_url' in sources[index]:
                                url = sources[index]['event_url']
                            else:
                                # Leave blank if source doesn't include them
                                url = ''
                            # next lets get the ID
                            if 'incident_number' in sources[index]:
                                # Set the incident Number
                                i_num = sources[index]['incident_number']
                            elif 'number' in sources[index]:
                                # Set the events number
                                i_num = sources[index]['number']
                            else:
                                # default to md5 hash of values list to ensure unique ID
                                i_num = hashlib.sha256(json.dumps(sources[index].values())).hexdigest()
                            # Now lets set the job additional parameters
                            additional = dict()
                            if 'parameters' in sources[index]['rule_processing'][rule_name]:
                                if isinstance(sources[index]['rule_processing'][rule_name]['parameters'], dict):
                                    additional = sources[index]['rule_processing'][rule_name]['parameters']
                                else:
                                    self._ioc.message().warning(
                                        "Parameters were not dictionary for rule: [" + str(rule_name) + "]"
                                    )
                            # Now lets setup the ticket info
                            additional['sn_ticket'] = i_num
                            self._ioc.message().debug(
                                "PREPARING TO SCHEDULE JOB [{0}] FOR EXECUTION::"
                                "EXE_ENV: [{1}] ADDITIONAL: [{2}] URL: [{3}] Incident_Number: [{4}]".format(
                                    str(rule_config['job']),
                                    str(exe_env),
                                    str(additional),
                                    str(url),
                                    str(i_num)
                                ),
                                True
                            )
                            if self._assign(rule_config['job'], exe_env, additional, url, i_num):
                                # we successfully assigned the ticket
                                self._ioc.message().debug(
                                    "JOB EXECUTION SCHEDULING SUCCESSFUL [{0}] FOR RULE [{1}]".format(
                                        str(index),
                                        str(rule_name)
                                    ),
                                    True
                                )
                                sources[index]['grease_internal_assigned'] = True
                                continue
                            else:
                                # we failed to assign the ticket
                                self._ioc.message().debug(
                                    "JOB EXECUTION SCHEDULING FAILED [{0}] FOR RULE [{1}]".format(
                                        str(index),
                                        str(rule_name)
                                    ),
                                    True
                                )
                                sources[index]['grease_internal_assigned'] = False
                                continue
                        else:
                            # rule failed fine then
                            self._ioc.message().debug(
                                "RULE FAILED FOR SOURCE [{0}] RULE [{1}]".format(
                                    str(index),
                                    str(rule_name)
                                ),
                                True
                            )
                            continue
                else:
                    # No rules were processed on this source
                    self._ioc.message().debug(
                        "RULE PROCESSING WAS EMPTY FOR SOURCE [{0}]".format(
                            str(index)
                        ),
                        True
                    )
                    continue

    def _assign(self, job, exec_env, additional={}, sn_link='', sn_ticket='', package=''):
        # type: (str, str, dict, str, str, str) -> bool
        # check to ensure this ticket isn't already on the schedule
        if len(sn_ticket) > 0:
            sql = """
                SELECT
                  *
                FROM
                  grease.job_queue jq
                WHERE
                  jq.sn_ticket_number = %s AND
                  (
                    (
                      jq.in_progress = FALSE AND 
                      jq.completed = FALSE
                    ) OR 
                    jq.in_progress = true
                  )
            """
            assignment_check = self._conn.query(sql, (sn_ticket,))
            if len(assignment_check) != 0:
                self._ioc.message().warning(
                    "Ticket Already in Job Queue for Execution Ticket: [" + str(sn_ticket) + "]"
                )
                return False
        sql = """
            SELECT
              js.id,
              js.host_name,
              js.jobs_assigned
            FROM
              grease.job_servers js
            WHERE
              js.execution_environment LIKE %s AND 
              js.active is true
            ORDER BY
              js.jobs_assigned
        """
        server_info = self._conn.query(sql, (exec_env,))
        if len(server_info) < 1:
            self._ioc.message().error("No Execution Environments Found For Job: [" + job + "]")
            return False
        server_info = server_info[0]
        sql = """
            SELECT
              job_config.id
            FROM
              grease.job_config
            WHERE
              job_config.command_module = %s AND
              job_config.command_name = %s
            ORDER BY job_config.id DESC
            LIMIT 1
        """
        job_id = self._conn.query(sql, (package, job,))
        if len(job_id) < 1:
            self._ioc.message().error(
                "No Jobs Configured For Requested Job: [" + job + "] for package: [" + package + "]"
            )
            return False
        job_id = job_id[0][0]
        sql = """
            INSERT INTO
              grease.job_queue
            (host_name, job_id, sn_ticket_number, sn_link, additional)
            VALUES
            (
              %s,
              %s,
              %s,
              %s,
              %s
            )
        """
        self._conn.execute(sql, (server_info[1], job_id, sn_ticket, sn_link, json.dumps(additional),))
        sql = """
            UPDATE
              grease.job_servers
            SET
              jobs_assigned = %s
            WHERE
              id = %s
        """
        self._conn.execute(sql, (int(server_info[2]) + 1, server_info[0],))
        self._ioc.message().debug(
            "JOB [{0}] SCHEDULED FOR SERVER [{1}]".format(
                str(job_id),
                str(server_info[1])
            ),
            True
        )
        return True

    def _take_ownership(self, source_file_id):
        # type: (int) -> None
        sql = """
            UPDATE
              grease.scheduling_queue
            SET
              in_progress = true,
              pick_up_time = current_timestamp
            WHERE
              id = %s
        """
        self._ioc.message().debug(
            "TAKING OWNERSHIP OF SOURCE [{0}]".format(
                str(source_file_id),
            ),
            True
        )
        self._conn.execute(sql, (source_file_id,))

    def _complete(self, source_file_id):
        # type: (int) -> None
        sql = """
            UPDATE
              grease.scheduling_queue
            SET
              completed = TRUE,
              in_progress = false,
              complete_time = current_timestamp
            WHERE
              id = %s
        """
        self._ioc.message().debug(
            "COMPLETING SOURCE [{0}]".format(
                str(source_file_id),
            ),
            True
        )
        self._conn.execute(sql, (source_file_id,))
