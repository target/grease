from tgt_grease_daemon.BaseCommand import GreaseDaemonCommand
from tgt_grease_core_util.Database import Connection
import datetime
import time


class Section31(GreaseDaemonCommand):
    def __init__(self):
        super(Section31, self).__init__()
        self._conn = Connection()

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
                  grease.job_queue jq
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
                    js.host_name,
                    count(jt.id) AS total
                  FROM
                    grease.job_servers js
                    LEFT OUTER JOIN grease.job_telemetry jt ON (jt.server_id = js.host_name)
                  GROUP BY js.host_name
              ),
              completed_daemon AS (
                SELECT
                  js.host_name,
                  count(jtd.id) AS total
                FROM
                  grease.job_servers js
                  LEFT OUTER JOIN grease.job_telemetry_daemon jtd ON (jtd.server_id = js.host_name)
                GROUP BY js.host_name
              ),
                sources AS (
                  SELECT
                    js.host_name,
                    count(sf.id) AS total
                  FROM
                    grease.source_file sf
                    INNER JOIN grease.job_servers js ON (js.id = sf.job_server)
                  WHERE
                    (
                      (
                        sf.in_progress = FALSE AND
                        sf.completed = FALSE
                      ) OR
                      sf.in_progress = TRUE
                    )
                  GROUP BY js.host_name
              ),
                schedules AS (
                  SELECT
                    js.host_name,
                    count(sq.id) AS total
                  FROM
                    grease.scheduling_queue sq
                    INNER JOIN grease.job_servers js ON (js.id = sq.job_server)
                  WHERE
                    (
                      (
                        sq.in_progress = FALSE AND
                        sq.completed = FALSE
                      ) OR
                      sq.in_progress = TRUE
                    )
                  GROUP BY js.host_name
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
              grease.job_servers js
              LEFT OUTER JOIN on_demand od ON (od.host_name = js.host_name)
              LEFT OUTER JOIN completed_on_demand cod ON (cod.host_name = js.host_name)
              LEFT OUTER JOIN completed_daemon coda ON (coda.host_name = js.host_name)
              LEFT OUTER JOIN sources s ON (s.host_name = js.host_name)
              LEFT OUTER JOIN schedules sch ON (sch.host_name = js.host_name)
            WHERE
              js.active IS TRUE
            ORDER BY js.id
        """
        return list(self._conn.query(sql))

    def _declare_doctor(self, server_id):
        # type: (int) -> None
        # first lets check to ensure someone hasn't already claimed this beast
        sql = """
            SELECT
              coalesce(doctor, '')
            FROM
              grease.server_health
            WHERE
              server_id = %s
        """
        result = self._conn.query(sql, (server_id,))
        if len(result) > 0 and result[0][0] is not '':
            self._ioc.message().error("SERVER DOCTOR ALREADY DECLARED FOR [{0}]".format(server_id))
            return
        sql = """
            UPDATE
              grease.server_health
            SET
              doctor = %s
            WHERE
              server_id = %s
        """
        self._conn.execute(sql, (self._grease_identity, server_id,))

    def _am_i_the_doctor(self, server_id):
        # type: (int) -> bool
        sql = """
            SELECT
              *
            FROM
              grease.server_health
            WHERE
              doctor = %s AND
              server_id = %s
        """
        result = self._conn.query(sql, (self._grease_identity, server_id,))
        if len(result) > 0:
            return True
        else:
            return False

    def _server_alive(self, server):
        # type: (list) -> bool
        sql = """
            SELECT
              sh.job_hash,
              sh.check_time
            FROM
              grease.server_health sh
            WHERE
              sh.server_id = %s
        """
        res = self._conn.query(sql, (server[0],))
        if len(res) is 0:
            # if this is a server not checked into health before
            self._register_in_health(server)
            res = self._conn.query(sql, (server[0],))[0]
        res = res[0]
        # now return to regular logic
        if res[1] < (datetime.datetime.now(res[1].tzinfo) - datetime.timedelta(hours=12)):
            # server status is old
            # lets check the hash though
            if res[0] == server[6]:
                # hash hasn't changed time for d-com
                return False
            else:
                # hash is old but changed, lets update and return True
                self._update_hash(server[0], server[6])
                return True
        else:
            # results aren't 12 hrs old yet
            if res[0] == server[6]:
                # log but do nothing so we know bad things will happen if we continue
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
        sql_ins = """
            INSERT INTO
              grease.server_health
            (server_id, job_hash, check_time)
            VALUES
            (%s, %s, current_timestamp)
        """
        self._conn.execute(sql_ins, (server[0], server[6],))

    def _update_hash(self, server_id, hash_str):
        # type: (str, str) -> None
        sql = """
            UPDATE
              grease.server_health
            SET
              job_hash = %s,
              check_time = current_timestamp
            WHERE
              server_id = %s
        """
        self._conn.execute(sql, (hash_str, server_id,))

    def _deactivate_server(self, server_id):
        # type: (int) -> None
        sql = """
                    UPDATE
                      grease.job_servers
                    SET
                      active = FALSE
                    WHERE
                      id = %s
                """
        self._conn.execute(sql, (server_id,))

    def _get_new_execution_server(self, server_id):
        # type: (int) -> list
        # first get current env
        sql = "SELECT execution_environment FROM grease.job_servers WHERE id = %s"
        exec_env = self._conn.query(sql, (server_id,))[0][0]
        sql = """
                    SELECT
                      js.id,
                      js.host_name
                    FROM
                      grease.job_servers js
                    WHERE
                      js.execution_environment = %s AND
                      js.active IS TRUE
                    ORDER BY
                      js.jobs_assigned
                    LIMIT 1
                """
        result = self._conn.query(sql, (exec_env,))
        if len(result) > 0:
            # we have a server to reassign to
            return result[0]
        else:
            # there are no other execution servers for that environment
            self._ioc.message().error(
                "No other valid execution environment for jobs assigned to server [{0}]".format(server_id)
            )
            return []

    def _cull_server(self, server_id):
        # type: (int) -> None
        self._ioc.message().warning("DEACTIVATING SERVER [{0}]".format(server_id))
        # first lets deactivate the job server
        self._deactivate_server(server_id)
        # next we need to check for any jobs scheduled to that instance and reassign them
        # first lets see if there is another available server
        server = self._get_new_execution_server(server_id)
        if len(server) > 0:
            # get the number of jobs being reassigned
            sql = """
                SELECT
                  array(
                    SELECT
                      jq.id
                    FROM
                      grease.job_queue jq
                    INNER JOIN grease.job_servers js ON (js.host_name = jq.host_name)
                    WHERE
                      js.id = %s AND
                      (
                        (
                          jq.in_progress = FALSE AND
                          jq.completed = FALSE
                        ) OR
                        jq.in_progress = TRUE
                      )
                  )
            """
            result = self._conn.query(sql, (server_id,))
            if len(result) > 0:
                # we have jobs to move
                # step one get the list of jobs to reassign
                job_id_group = tuple(result[0][0])
                self._reassign_on_demand_jobs(server_id, server, job_id_group)
            else:
                self._ioc.message().info("No jobs to reassign for server [{0}] being decommissioned".format(server_id))
        else:
            # no other valid server could be found for on-demand work
            self._ioc.message().error("Failed reassigning jobs for server [{0}]".format(server_id))
        # next lets move over any source detection work
        sql = """
            SELECT
              array (
                SELECT
                  sf.id
                FROM
                  grease.source_file sf
                WHERE
                  sf.job_server = %s AND
                  in_progress IS FALSE AND
                  completed IS FALSE
              )
        """
        source_file_jobs = tuple(self._conn.query(sql, (server_id,))[0][0])
        if len(source_file_jobs):
            # we have sources to reassign parsing for
            self._reassign_sources(source_file_jobs, server_id)
        else:
            # no source documents to reassign
            self._ioc.message().info("No source parsing to reassign for server [{0}]".format(server_id))
        # finally lets worry about schedules to be reassigned
        sql = """
            SELECT
              array (
                SELECT
                  sq.id
                FROM
                  grease.scheduling_queue sq
                WHERE
                  sq.job_server = %s AND
                  in_progress IS FALSE AND
                  completed IS FALSE
              )
        """
        schedules = tuple(self._conn.query(sql, (server_id,))[0][0])
        if len(schedules):
            # we have sources to reassign parsing for
            self._reassign_schedules(schedules, server_id)
        else:
            # no source documents to reassign
            self._ioc.message().info("No schedules to reassign for server [{0}]".format(server_id))

    def _reassign_on_demand_jobs(self, server_id, new_server, job_list):
        # type: (int, list, tuple) -> None
        # now lets do the update
        if not job_list:
            job_list = (-1,)
        sql = """
            UPDATE
              grease.job_queue
            SET
              host_name = %s
            WHERE
              id IN %s
        """
        self._conn.execute(sql, (new_server[1], job_list,))
        # now lets update the totals on the job servers in question
        self._update_job_assignment_totals(server_id, new_server[0], len(job_list))
        self._ioc.message().info(
            "JOB ID SET [{0}] MOVED FROM SERVER [{1}] TO SERVER [{2}]".format(
                job_list,
                server_id,
                new_server[0]
            )
        )

    def _reassign_sources(self, source_file_ids, origin_server):
        # type: (tuple, int) -> None
        # first lets find our applicable detector server
        sql = """
            SELECT
              js.id
            FROM
              grease.job_servers js
            WHERE
              js.active is TRUE AND
              js.detector is TRUE
            ORDER BY
              js.jobs_assigned
        """
        result = self._conn.query(sql)
        if len(result) > 0:
            new_server = result[0]
            reassign_total = len(source_file_ids)
            # Actual reassignment of sources
            sql = """
                UPDATE
                  grease.source_file
                SET
                  job_server = %s
                WHERE
                  id IN %s
            """
            self._conn.execute(sql, (new_server[0], source_file_ids))
            self._update_job_assignment_totals(origin_server, new_server[0], reassign_total)
        else:
            # oh crap we have no job detector servers left alive
            # Me IRL Right now:
            # https://68.media.tumblr.com/e59c51080e14cee56ce93416cf8055c8/tumblr_mzncp3nYXh1syplf0o1_250.gif
            # TODO: Alert via side channel
            self._ioc.message().error(
                "NO AVAILABLE DETECTOR SERVER CANNOT REASSIGN JOBS [{0}] FROM SERVER [{1}]".format(
                    source_file_ids, origin_server
                )
            )
            # bail because we have no one to reassign to
            return

    def _reassign_schedules(self, schedule_ids, origin_server):
        # type: (tuple, int) -> None
        # first lets find our applicable detector server
        sql = """
            SELECT
              js.id
            FROM
              grease.job_servers js
            WHERE
              js.active is TRUE AND
              js.scheduler is TRUE
            ORDER BY
              js.jobs_assigned
        """
        result = self._conn.query(sql)
        if len(result) > 0:
            new_server = result[0]
            reassign_total = len(schedule_ids)
            # Actual reassignment of sources
            sql = """
                UPDATE
                  grease.source_file
                SET
                  job_server = %s
                WHERE
                  id IN %s
            """
            self._conn.execute(sql, (new_server[0], schedule_ids))
            self._update_job_assignment_totals(origin_server, new_server[0], reassign_total)
        else:
            # oh crap we have no job scheduler servers left alive
            # Me IRL Right now: https://media.giphy.com/media/HUkOv6BNWc1HO/giphy.gif
            # TODO: Alert via side channel
            self._ioc.message().error(
                "NO AVAILABLE SCHEDULER SERVER CANNOT REASSIGN JOBS [{0}] FROM SERVER [{1}]".format(
                    schedule_ids, origin_server
                )
            )
            # bail because we have no one to reassign to
            return

    def _update_job_assignment_totals(self, old_server, new_server, job_count):
        # type: (int, int, int) -> None
        # first lets deduct from the bad server
        sql = """
            UPDATE
              grease.job_servers
            SET
              jobs_assigned = (jobs_assigned - %s)
            WHERE
              id = %s
        """
        self._conn.execute(sql, (job_count, old_server,))
        # now lets increase the good job server
        sql = """
            UPDATE
              grease.job_servers
            SET
              jobs_assigned = (jobs_assigned + %s)
            WHERE
              id = %s
        """
        self._conn.execute(sql, (job_count, new_server,))
