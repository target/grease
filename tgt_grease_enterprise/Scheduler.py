from tgt_grease_daemon.BaseCommand import GreaseDaemonCommand
from tgt_grease_enterprise.Detectors import DetectorConfiguration
from tgt_grease_core_util import SQLAlchemyConnection, Configuration
from tgt_grease_core_util.RDBMSTypes import JobServers, SourceData, JobConfig, JobQueue
from sqlalchemy import and_, update, or_
from datetime import datetime
import json
import hashlib


class Scheduler(GreaseDaemonCommand):
    def __init__(self):
        super(Scheduler, self).__init__()
        self._scanner_config = DetectorConfiguration.ConfigurationLoader()
        self._config = Configuration()
        self._sql = SQLAlchemyConnection(self._config)

    def execute(self, context='{}'):
        # Lets go get the jobs needing to be scheduled by this server
        result = self._sql.get_session().query(SourceData, JobServers)\
            .filter(SourceData.scheduling_server == JobServers.id)\
            .filter(JobServers.id == self._config.node_db_id())\
            .filter(SourceData.detection_start_time != None)\
            .filter(SourceData.detection_end_time != None)\
            .filter(SourceData.detection_complete == True)\
            .filter(SourceData.scheduling_start_time == None)\
            .filter(SourceData.scheduling_end_time == None)\
            .filter(SourceData.scheduling_complete == False)\
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
                            additional['ticket'] = i_num
                            self._ioc.message().debug(
                                "PREPARING TO SCHEDULE JOB [{0}] FOR EXECUTION::"
                                "EXE_ENV: [{1}] ADDITIONAL: [{2}] ticket: [{3}]".format(
                                    str(rule_config['job']),
                                    str(exe_env),
                                    str(additional),
                                    str(i_num)
                                ),
                                True
                            )
                            if self._assign(
                                    rule_config['job'],
                                    exe_env,
                                    str(self._config.get('SCHEDULE_PKG', 'localhost_generic')),
                                    str(i_num),
                                    additional
                            ):
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

    def _assign(self, job, exec_env, package, ticket, additional=dict):
        # type: (str, str, str, str, dict) -> bool
        # check to ensure this ticket isn't already on the schedule
        if len(ticket) > 0:
            result = self._sql.get_session().query(JobQueue)\
                .filter(JobQueue.ticket == ticket)\
                .filter(or_(and_(JobQueue.in_progress == False, JobQueue.completed == False), JobQueue.in_progress == True))\
                .all()
            if result:
                self._ioc.message().warning(
                    "Ticket Already in Job Queue for Execution Ticket: [" + str(ticket) + "]"
                )
                return False
        # lets only get the least assigned server so we can round robin
        result = self._sql.get_session()\
            .query(JobServers)\
            .filter(JobServers.execution_environment == exec_env)\
            .filter(JobServers.active == True)\
            .order_by(JobServers.jobs_assigned)\
            .first()
        if not result:
            self._ioc.message().error("No Execution Environments Found For Job: [" + job + "]")
            return False
        server_info = result.id
        result = self._sql.get_session().query(JobConfig)\
            .filter(JobConfig.command_module == package)\
            .filter(JobConfig.command_name == job)\
            .first()
        if not result:
            self._ioc.message().error(
                "No Jobs Configured For Requested Job: [" + job + "] for package: [" + package + "]"
            )
            return False
        job_id = result.id
        # Proceed to schedule
        JobToQueue = JobQueue(
            host_name=server_info,
            job_id=job_id,
            ticket=ticket,
            additional=additional
        )
        self._sql.get_session().add(JobToQueue)
        self._sql.get_session().commit()
        # that job and increment the assignment counter
        stmt = update(JobServers).where(JobServers.id == server_info).values(jobs_assigned=result.jobs_assigned + 1)
        self._sql.get_session().execute(stmt)
        self._sql.get_session().commit()
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
        stmt = update(SourceData)\
            .where(SourceData.id == source_file_id)\
            .values(scheduling_start_time=datetime.utcnow())
        self._sql.get_session().execute(stmt)
        self._sql.get_session().commit()
        self._ioc.message().debug(
            "TAKING OWNERSHIP OF SOURCE [{0}]".format(
                str(source_file_id),
            ),
            True
        )

    def _complete(self, source_file_id):
        # type: (int) -> None
        stmt = update(SourceData)\
            .where(SourceData.id == source_file_id)\
            .values(scheduling_complete=True, scheduling_end_time=datetime.utcnow())
        self._sql.get_session().execute(stmt)
        self._sql.get_session().commit()
        self._ioc.message().debug(
            "COMPLETING SOURCE [{0}]".format(
                str(source_file_id),
            ),
            True
        )
