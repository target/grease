from tgt_grease_daemon.BaseCommand import GreaseDaemonCommand
from tgt_grease_core_util.Database import SQLAlchemyConnection
from tgt_grease_core_util import Configuration
from tgt_grease_core_util.RDBMSTypes import JobServers, JobQueue,SourceData, ServerHealth
from sqlalchemy import update, and_, or_
import datetime
import time


class Section31(GreaseDaemonCommand):
    def __init__(self):
        super(Section31, self).__init__()
        self._config = Configuration()
        self._sql = SQLAlchemyConnection(self._config)

    def execute(self, context='{}'):
        # first lets get the entire farm
        farm = self._get_farm_status()
        # now lets check each server from the last known state
        for server in farm:
            if self._server_alive(server):
                # server seems to be alive keep going
                continue
            else:
                # server is not alive, we need to migrate work from it
                # first lets declare ourselves as the doctor
                self._declare_doctor(server[0])
                # now lets sleep to ensure we don't stop on other doctors
                time.sleep(10)
                # okay lets ensure we are still the doctor
                if self._am_i_the_doctor(server[0]):
                    # time to reassign
                    self._cull_server(server[0])
                else:
                    # during our slumber someone else decided to work on this server let them have it
                    continue
        return True

    def _get_farm_status(self):
        # type: () -> list
        sql = """
            WITH on_demand AS (
                SELECT
                  jq.host_name,
                  count(jq.id) AS total
                FROM
                  job_queue jq
                WHERE
                  (
                    (
                      jq.in_progress = FALSE AND
                      jq.completed = FALSE
                    ) OR
                    jq.in_progress = TRUE
                  )
                GROUP BY jq.host_name
              ),
                completed_on_demand AS (
                  SELECT
                    jt.server_id as host_name,
                    count(jt.id) AS total
                  FROM
                    job_servers js
                    LEFT OUTER JOIN job_telemetry jt ON (jt.server_id = js.id)
                  GROUP BY jt.server_id
              ),
              completed_daemon AS (
                SELECT
                  js.id as host_name,
                  count(jtd.id) AS total
                FROM
                  job_servers js
                  LEFT OUTER JOIN job_telemetry_daemon jtd ON (jtd.server_id = js.id)
                GROUP BY js.id
              ),
                sources AS (
                  SELECT
                    js.id as host_name,
                    count(sf.id) AS total
                  FROM
                    source_data sf
                    INNER JOIN grease.job_servers js ON (js.id = sf.detection_server)
                  WHERE
                    (
                      (
                        sf.detection_start_time IS NOT NULL AND
                        sf.detection_end_time IS NOT NULL
                      ) OR
                      (
                        sf.detection_start_time IS NOT NULL AND
                        sf.detection_end_time IS NULL
                      )
                    )
                  GROUP BY js.id
              ),
                schedules AS (
                  SELECT
                    js.id as host_name,
                    count(sq.id) AS total
                  FROM
                    source_data sq
                    INNER JOIN grease.job_servers js ON (js.id = sq.scheduling_server)
                  WHERE
                    (
                      (
                        sq.scheduling_start_time IS NOT NULL AND
                        sq.scheduling_end_time IS NOT NULL
                      ) OR
                      (
                        sq.scheduling_start_time IS NOT NULL AND
                        sq.scheduling_end_time IS NULL
                      )
                    )
                  GROUP BY js.id
              )
            SELECT
              js.id                    AS job_server_id,
              js.host_name,
              coalesce(od.total, 0)    AS on_demand_total,
              coalesce((cod.total + coda.total), 0)   AS completed_total,
              coalesce(s.total, 0)     AS sources,
              coalesce(sch.total, 0)   AS schedules,
              (coalesce(od.total, 0) || '-' || coalesce((cod.total + coda.total), 0) || '-' || coalesce(s.total, 0) || '-' ||
               coalesce(sch.total, 0)) AS str_hash
            FROM
              job_servers js
              LEFT OUTER JOIN on_demand od ON (od.host_name = js.id)
              LEFT OUTER JOIN completed_on_demand cod ON (cod.host_name = js.id)
              LEFT OUTER JOIN completed_daemon coda ON (coda.host_name = js.id)
              LEFT OUTER JOIN sources s ON (s.host_name = js.id)
              LEFT OUTER JOIN schedules sch ON (sch.host_name = js.id)
            WHERE
              js.active IS TRUE
            ORDER BY js.id
        """
        return list(self._sql.get_engine().execute(sql).fetchall())

    def _declare_doctor(self, server_id):
        # type: (int) -> None
        # first lets check to ensure someone hasn't already claimed this beast
        result = self._sql.get_session().query(ServerHealth)\
            .filter(ServerHealth.server == server_id)\
            .first()
        if result and result.doctor != '':
            self._ioc.message().error("SERVER DOCTOR ALREADY DECLARED FOR [{0}]".format(server_id))
            return
        stmt = update(ServerHealth).where(ServerHealth.server == server_id).values(docter=self._config.node_db_id())
        self._sql.get_session().execute(stmt)
        self._sql.get_session().commit()

    def _am_i_the_doctor(self, server_id):
        # type: (int) -> bool
        result = self._sql.get_session().query(ServerHealth)\
            .filter(ServerHealth.doctor == self._config.node_db_id())\
            .filter(ServerHealth.server == server_id)\
            .first()
        if result:
            return True
        else:
            return False

    def _server_alive(self, server):
        # type: (list) -> bool
        result = self._sql.get_session().query(ServerHealth)\
            .filter(ServerHealth.server == server[0])\
            .first()
        if not result:
            # if this is a server not checked into health before
            self._register_in_health(server[0])
            result = self._sql.get_session().query(ServerHealth)\
                .filter(ServerHealth.server == server[0])\
                .first()
        # now return to regular logic
        if result.check_time < (datetime.datetime.now(result.check_time.tzinfo) - datetime.timedelta(hours=6)):
            # server status is old
            # lets check the hash though
            if result.job_hash == server[6]:
                # hash hasn't changed time for d-com
                return False
            else:
                # hash is old but changed, lets update and return True
                self._update_hash(server[0], server[6])
                return True
        else:
            # results aren't 12 hrs old yet
            if result.job_hash == server[6]:
                # log but do nothing so we know bad things will happen if we continue
                if result.check_time < (datetime.datetime.now(result.check_time.tzinfo) - datetime.timedelta(minutes=10)):
                    self._ioc.message().warning(
                        "Server hash has not changed since last poll ID:[{0}] hash:[{1}]".format(
                            server[0],
                            server[6]
                        )
                    )
            else:
                # if it changed lets update so we see the current hash
                self._update_hash(server[0], server[6])
            return True

    def _register_in_health(self, server):
        newServer = ServerHealth(
            server=server[0],
            job_hash=server[6],
            check_time=datetime.datetime.utcnow()
        )
        self._sql.get_session().add(newServer)
        self._sql.get_session().commit()

    def _update_hash(self, server_id, hash_str):
        # type: (str, str) -> None
        stmt = update(ServerHealth)\
            .where(ServerHealth.server == server_id)\
            .values(job_hash=hash_str, check_time=datetime.datetime.utcnow())
        self._sql.get_session().execute(stmt)
        self._sql.get_session().commit()

    def _deactivate_server(self, server_id):
        # type: (int) -> None
        stmt = update(JobServers)\
            .where(JobServers.id == server_id)\
            .values(active=False)
        self._sql.get_session().execute(stmt)
        self._sql.get_session().commit()

    def _get_new_execution_server(self, server_id):
        # type: (int) -> JobServers
        # first get current env
        old_server = self._sql.get_session().query(JobServers)\
            .filter(JobServers.id == server_id)\
            .first()
        new_server = self._sql.get_session().query(JobServers)\
            .filter(JobServers.execution_environment == old_server.execution_environment)\
            .filter(JobServers.active == True)\
            .order_by(JobServers.jobs_assigned)\
            .first()
        if new_server:
            # we have a server to reassign to
            return new_server
        else:
            # there are no other execution servers for that environment
            self._ioc.message().error(
                "No other valid execution environment for jobs assigned to server [{0}]".format(server_id),
                hipchat=True
            )
            return False

    def _cull_server(self, server_id):
        # type: (int) -> None
        self._ioc.message().warning("DEACTIVATING SERVER [{0}]".format(server_id), hipchat=True)
        # first lets deactivate the job server
        self._deactivate_server(server_id)
        # next we need to check for any jobs scheduled to that instance and reassign them
        # first lets see if there is another available server
        server = self._get_new_execution_server(server_id)
        if server:
            # get the number of jobs being reassigned
            result = self._sql.get_session().query(JobQueue) \
                .filter(or_(and_(JobQueue.in_progress == False, JobQueue.completed == False), JobQueue.in_progress == True)) \
                .filter(JobQueue.host_name == server_id)\
                .all()
            if result:
                jobs = []
                for job in result:
                    jobs.append(job.id)
                # we have jobs to move
                # step one get the list of jobs to reassign
                job_id_group = tuple(jobs)
                self._reassign_on_demand_jobs(server_id, server.id, job_id_group)
            else:
                self._ioc.message().info("No jobs to reassign for server [{0}] being decommissioned".format(server_id))
        else:
            # no other valid server could be found for on-demand work
            self._ioc.message().error("Failed reassigning jobs for server [{0}]".format(server_id))
        # next lets move over any source detection work
        result = self._sql.get_session().query(SourceData)\
            .filter(SourceData.detection_server == server_id)\
            .filter(SourceData.detection_start_time == None)\
            .filter(SourceData.detection_end_time == None)\
            .filter(SourceData.detection_complete == False)\
            .all()
        jobs = []
        for job in result:
            jobs.append(job.id)
        source_file_jobs = tuple(jobs)
        if len(source_file_jobs):
            # we have sources to reassign parsing for
            self._reassign_sources(source_file_jobs, server_id)
        else:
            # no source documents to reassign
            self._ioc.message().info("No source parsing to reassign for server [{0}]".format(server_id))
        # finally lets worry about schedules to be reassigned
        result = self._sql.get_session().query(SourceData) \
            .filter(SourceData.scheduling_server == server_id) \
            .filter(SourceData.detection_start_time != None)\
            .filter(SourceData.detection_end_time != None)\
            .filter(SourceData.detection_complete == True)\
            .filter(SourceData.scheduling_start_time == None)\
            .filter(SourceData.scheduling_end_time == None)\
            .filter(SourceData.scheduling_complete == False)\
            .all()
        jobs = []
        for job in result:
            jobs.append(job.id)
        schedules = tuple(jobs)
        if len(schedules):
            # we have sources to reassign parsing for
            self._reassign_schedules(schedules, server_id)
        else:
            # no source documents to reassign
            self._ioc.message().info("No schedules to reassign for server [{0}]".format(server_id))

    def _reassign_on_demand_jobs(self, server_id, new_server, job_list):
        # type: (int, int, tuple) -> None
        # now lets do the update
        if not job_list:
            job_list = (-1,)
        stmt = update(JobQueue)\
            .where(JobQueue.id.in_(job_list))\
            .values(host_name=new_server)
        self._sql.get_session().execute(stmt)
        self._sql.get_session().commit()
        # now lets update the totals on the job servers in question
        self._update_job_assignment_totals(server_id, new_server, len(job_list))
        self._ioc.message().info(
            "JOB ID SET [{0}] MOVED FROM SERVER [{1}] TO SERVER [{2}]".format(
                job_list,
                server_id,
                new_server
            )
        )

    def _reassign_sources(self, source_file_ids, origin_server):
        # type: (tuple, int) -> None
        # first lets find our applicable detector server
        result = self._sql.get_session().query(JobServers)\
            .filter(JobServers.active == True)\
            .filter(JobServers.detector == True)\
            .order_by(JobServers.jobs_assigned)\
            .first()
        if result:
            new_server = result.id
            reassign_total = len(source_file_ids)
            # Actual reassignment of sources
            stmt = update(SourceData)\
                .where(SourceData.id.in_(source_file_ids))\
                .values(detection_server=new_server)
            self._sql.get_session().execute(stmt)
            self._sql.get_session().commit()
            self._update_job_assignment_totals(origin_server, new_server, reassign_total)
        else:
            # oh crap we have no job detector servers left alive
            # Me IRL Right now:
            # https://68.media.tumblr.com/e59c51080e14cee56ce93416cf8055c8/tumblr_mzncp3nYXh1syplf0o1_250.gif
            self._ioc.message().error(
                "NO AVAILABLE DETECTOR SERVER CANNOT REASSIGN JOBS [{0}] FROM SERVER [{1}]".format(
                    source_file_ids, origin_server
                ),
                hipchat=True
            )
            # bail because we have no one to reassign to
            return

    def _reassign_schedules(self, schedule_ids, origin_server):
        # type: (tuple, int) -> None
        # first lets find our applicable scheduling server
        result = self._sql.get_session().query(JobServers)\
            .filter(JobServers.active == True)\
            .filter(JobServers.scheduler == True)\
            .order_by(JobServers.jobs_assigned)\
            .first()
        if result:
            new_server = result.id
            reassign_total = len(schedule_ids)
            # Actual reassignment of sources
            stmt = update(SourceData)\
                .where(SourceData.id.in_(schedule_ids))\
                .values(scheduling_server=new_server)
            self._sql.get_session().execute(stmt)
            self._sql.get_session().commit()
            self._update_job_assignment_totals(origin_server, new_server, reassign_total)
        else:
            # oh crap we have no job scheduler servers left alive
            # Me IRL Right now: https://media.giphy.com/media/HUkOv6BNWc1HO/giphy.gif
            self._ioc.message().error(
                "NO AVAILABLE SCHEDULER SERVER CANNOT REASSIGN JOBS [{0}] FROM SERVER [{1}]".format(
                    schedule_ids, origin_server
                ),
                hipchat=True
            )
            # bail because we have no one to reassign to
            return

    def _update_job_assignment_totals(self, old_server, new_server, job_count):
        # type: (int, int, int) -> None
        # first lets deduct from the bad server
        stmt1 = update(JobServers)\
            .where(id=old_server)\
            .values(jobs_assigned=JobServers.jobs_assigned - job_count)
        stmt2 = update(JobServers)\
            .where(id=new_server)\
            .values(jobs_assigned=JobServers.jobs_assigned + job_count)
        self._sql.get_session().execute(stmt1)
        self._sql.get_session().execute(stmt2)
        self._sql.get_session().commit()
