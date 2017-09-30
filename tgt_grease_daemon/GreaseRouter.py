from tgt_grease_core import GreaseRouter
from tgt_grease_daemon import BaseCommand
from tgt_grease_core_util.GreaseUtility import Grease
from tgt_grease_core_util.Database import Connection
from tgt_grease_core_util.ImportTools import Importer
import datetime
from . import Daemon
import os
import commands
from collections import deque
import sys

# PyWin32
if os.name == 'nt':
    import win32event


class Router(GreaseRouter.Router):
    def __init__(self):
        GreaseRouter.Router.__init__(self)
        self._runs = 0
        self._run_throttle_tick = 0
        self._persistent_job_completed_queue = []
        self._current_real_second = datetime.datetime.now().second
        self._current_run_second = datetime.datetime.now().second
        self._conn = Connection()
        self._total_normal_jobs = 0
        self._importer = Importer(self._get_ioc().message())
        if os.name == 'nt':
            self._identity_file = "C:\grease\grease_identity.txt"
        else:
            self._identity_file = "/tmp/grease/grease_identity.txt"
        if os.path.isfile(self._identity_file):
            self._grease_identity = str(open(self._identity_file, 'r').read()).rstrip()
        else:
            self._grease_identity = ''
        self._process = None

    def _set_run_throttle_tick(self, count):
        # type: (int) -> None
        self._run_throttle_tick = int(count)

    def _get_run_throttle_tick(self):
        # type: () -> int
        return int(self._run_throttle_tick)

    def _inc_run_throttle_tick(self):
        self._run_throttle_tick += 1

    def _reset_run_throttle_tick(self):
        self._run_throttle_tick = 0

    def _set_process(self, proc):
        # type: (Daemon) -> None
        self._process = proc
        return None

    def _get_process(self):
        return self._process

    def _get_total_normal_jobs(self):
        # type: () -> int
        return int(self._total_normal_jobs)

    def _set_total_normal_jobs(self, total):
        # type: () -> None
        self._total_normal_jobs = int(total)

    def _get_ioc(self):
        # type: () -> Grease
        return self._grease

    def _get_run_count(self):
        # type: () -> int
        return self._runs

    def _inc_run_count(self):
        # type: () -> None
        self._runs += 1

    def _clear_persistent_jobs_run(self):
        # type: () -> None
        self._persistent_job_completed_queue = []

    def _add_persistent_job_run(self, job_id):
        # type: (int) -> None
        if str(job_id) not in self._persistent_job_completed_queue:
            self._persistent_job_completed_queue.append(str(job_id))

    def _remove_persistent_job_run(self, job_id):
        # type: (int) -> None
        self._persistent_job_completed_queue.remove(str(job_id))

    def _has_persistent_job_run(self, job_id):
        # type: (int) -> bool
        if str(job_id) in self._persistent_job_completed_queue:
            return True
        else:
            return False

    @staticmethod
    def _get_current_real_second():
        # type: () -> int
        return datetime.datetime.now().second

    def _get_current_run_second(self):
        # type: () -> int
        return int(self._current_run_second)

    def _set_current_run_second(self, sec):
        # type: (int) -> None
        self._current_run_second = int(sec)

    def _have_we_moved_forward_in_time(self):
        # type: () -> bool
        # Look I know this is a long method name
        # but it reads well and makes sense
        # so if this is a problem, fine
        if self._get_current_run_second() == self._get_current_real_second():
            return False
        else:
            self._set_current_run_second(self._get_current_real_second())
            self._clear_persistent_jobs_run()
            self._reset_run_throttle_tick()
            return True

    def _get_conn(self):
        # type: () -> Connection
        return self._conn

    @staticmethod
    def entry_point():
        router = Router()
        router.gateway()

    def gateway(self):
        if len(self.args) <= 2:
            if os.name == 'nt':
                self._set_process(Daemon.WindowsService(sys.argv, self))
            else:
                self._set_process(Daemon.UnixDaemon(self))
            if self.args[0] == 'start':
                self._get_ioc().message().debug("Starting Daemon")
                self._get_process().start()
            elif self.args[0] == 'restart':
                self._get_ioc().message().debug("Restarting Daemon")
                self._get_process().restart()
            elif self.args[0] == 'stop':
                self._get_ioc().message().debug("Stopping Daemon")
                self._get_process().stop()
            else:
                self.bad_exit("Invalid Command To Daemon expected [start,stop,restart]", 2)
        else:
            self.bad_exit("Command not given to daemon! Expected: [start,stop,restart]", 1)

    def _self_update_check(self):
        # type: () -> None
        # simple check if a daemon reload is requested
        if os.name == 'nt':
            req_file = "C:\\grease\\daemon_reload.run"
        else:
            req_file = "/tmp/grease/daemon_reload.run"
        if os.path.isfile(req_file):
            # first lets unset the file so we don't inf loop ourselves
            os.remove(req_file)
            # Now we are going to kill ourself so... yeah
            self._get_ioc().message().warning("SELF UPDATE DETECTED REBOOTING DAEMON")
            self._get_ioc().message().debug(str(commands.getstatusoutput('grease-daemon stop && grease-daemon start')))

    def job_processor(self, PyWinObj=None):
        # This is where the magic happens
        # Basic rc assignment before the loop
        rc = "Garbage"
        while True:
            # Windows Signal Catching
            if os.name == 'nt':
                if not rc != win32event.WAIT_OBJECT_0:
                    self._get_ioc().message().debug("Windows Kill Signal Detected! Closing GREASE")
                    break
            # Continue processing if daemon gets no signal
            # Process Throttling
            self._inc_run_throttle_tick()
            if os.getenv('GREASE_THROTTLE'):
                if int(self._get_run_throttle_tick()) > int(os.getenv('GREASE_THROTTLE', 10000)):
                    # prevent more than 1000 loops per second by default
                    # check time
                    self._have_we_moved_forward_in_time()
                    continue
            # first check to see if auto-update kicked
            self._self_update_check()
            # Now lets do stuff
            # Engage the Warp Nacelle
            # Get the run schedule
            job_schedule = self.get_jobs()
            # If we have no jobs to run
            if len(job_schedule) is 0:
                # have we moved forward since the last second
                if self._have_we_moved_forward_in_time():
                    # if we have we can log since the log does not have a record for this second
                    self._get_ioc().message().debug("Total Jobs To Process: [0] Current Runs: [{0}]".format(
                        str(self._get_run_count()))
                    )
                    # We also ensure we record we already logged for zero jobs to process this second
                    self._add_persistent_job_run(-1)
                else:
                    # we have not moved forward in time
                    # have we logged for this second
                    if not self._has_persistent_job_run(-1):
                        # We have not logged for this second so lets do that now
                        self._get_ioc().message().debug("Total Jobs To Process: [0] Current Runs: [{0}]".format(
                            str(self._get_run_count()))
                        )
                        # record that we logged for this second
                        self._add_persistent_job_run(-1)
            else:
                # time for high speed now we got some jobs to do
                # first lets record how many we need to do
                if self._get_total_normal_jobs() > 0:
                    # if we have any normal jobs lets log
                    self._get_ioc().message().debug("Total Jobs To Process: [{0}] Current Runs: [{1}]".format(
                        str(self._get_total_normal_jobs()),
                        str(self._get_run_count())
                        )
                    )
                else:
                    # we only have persistent jobs to process
                    # have we moved forward since the last second
                    if self._have_we_moved_forward_in_time():
                        # if we have we can log since the log does not have a record for this second
                        self._get_ioc().message().debug("Total Jobs To Process: [{0}] Current Runs: [{1}]".format(
                            str(len(job_schedule)),
                            str(self._get_run_count()))
                        )
                        # We also ensure we record we already logged for zero jobs to process this second
                        self._add_persistent_job_run(0)
                    else:
                        # we have not moved forward in time
                        # have we logged for this second
                        if not self._has_persistent_job_run(0):
                            # We have not logged for this second so lets do that now
                            self._get_ioc().message().debug("Total Jobs To Process: [{0}] Current Runs: [{1}]".format(
                                str(len(job_schedule)),
                                str(self._get_run_count()))
                            )
                            # record that we logged for this second
                            self._add_persistent_job_run(0)
                # now lets loop through the schedule and do some stuff
                for job in job_schedule:
                    # first lets ensure this job is to be run this cycle
                    # first lets execute all jobs that are On-demand (Non Persistent)
                    # This job is meant to run this cycle
                    # first if its a regular job lets just run through it
                    if str(job['persistent_job']).lower() == 'false':
                        # lets try to create this job
                        job_mod = str(job['module']).encode('utf-8')
                        job_comm = str(job['command']).encode('utf-8')
                        command_obj = self._importer.load(job_mod, job_comm)
                        # lets ensure this is a valid command object
                        if not isinstance(command_obj, BaseCommand.GreaseDaemonCommand):
                            # we don't have a valid command, time to fail this job
                            self._grease.message().error(
                                "Invalid Job Configuration for ID# [{0}]".format(str(job['id'])))
                            # we don't fail persistent jobs, they're persistent
                            if not job['persistent_job']:
                                self.job_failure(job['id'])
                            continue
                        self._get_ioc().message().debug('Executing On-Demand Command [{0}]'.format(
                            str(type(command_obj).__name__))
                        )
                        command_obj.attempt_execution(int(job['command_id']), job['additional'])
                    else:
                        if self._get_current_run_second() % int(job['tick']) is not 0:
                            # this means its not configured to run this time
                            continue
                        else:
                            if str(job['persistent_job']).lower() == 'true':
                                # We Have a job on this one to run every cycle its ready (a persistent job)
                                # ensure it hasn't run this cycle
                                if self._has_persistent_job_run(job['id']):
                                    # we've already done this one time in this second so skip
                                    # delete the command object since we are done with it
                                    self._add_persistent_job_run(job['id'])
                                    # new job time
                                    continue
                                else:
                                    # LETS BURN THIS CANDLE
                                    # lets try to create this job
                                    job_mod = str(job['module']).encode('utf-8')
                                    job_comm = str(job['command']).encode('utf-8')
                                    command_obj = self._importer.load(job_mod, job_comm)
                                    # lets ensure this is a valid command object
                                    if not isinstance(command_obj, BaseCommand.GreaseDaemonCommand):
                                        # we don't have a valid command, time to fail this job
                                        self._grease.message().error(
                                            "Invalid Job Configuration for ID# {0}".format(str(job['id'])))
                                        continue
                                    # lets log we are running a persistent job
                                    self._get_ioc().message().debug('Executing Persistent Command [{0}]'.format(
                                        str(type(command_obj).__name__))
                                    )
                                    command_obj.attempt_execution(int(job['command_id']), job['additional'])
                                    self._add_persistent_job_run(job['id'])
                            else:
                                # Probably Null checking the database is borked
                                self._get_ioc().message().error(
                                    "Invalid Job Persistent Configuration Returned! ID: {0} Expected True/False Got: "
                                    "[{1}] "
                                    .format(job['id'], job['persistent_job'])
                                )
                                continue
                    # Now lets run our telemetry
                    self._get_ioc().run_daemon_telemetry(command_obj)
                    # finally lets do some logging around the job outcome
                    if command_obj.get_exe_state()['result']:
                        if job['persistent_job']:
                            self._grease.message().debug("Persistent Job Successful [{0}]".format(str(job['id'])))
                        else:
                            self._grease.message().debug("On-Demand Job Successful [{0}]".format(str(job['id'])))
                        # we don't resolve persistent jobs, they're persistent
                        if not job['persistent_job']:
                            self.resolve_job(job['id'])
                    else:
                        if job['persistent_job']:
                            self._grease.message().warning("Persistent Job Failed [{0}]".format(str(job['id'])))
                        else:
                            self._grease.message().warning("On-Demand Job Failed [{0}]".format(str(job['id'])))
                        # we don't fail persistent jobs, they're persistent
                        if not job['persistent_job'] and not command_obj.get_exe_state()['execution']:
                            self.job_failure(job['id'])
                    # delete the command object since we are done with it
                    command_obj.__del__()
                    del command_obj
            # after all this its time to increment the run counter
            self._inc_run_count()
            # check time
            self._have_we_moved_forward_in_time()
            # After all this check for new windows services 
            if os.name == 'nt':
                # Block .5ms to listen for exit sig
                rc = win32event.WaitForSingleObject(PyWinObj.hWaitStop, 50)

    def get_jobs(self):
        # type: () -> deque
        SQL = """
            (
              SELECT
                pj.id,
                jc1.command_module as module,
                jc1.command_name as command,
                current_timestamp as request_time,
                pj.host_name,
                pj.additional,
                jc1.id as command_id,
                false as is_threaded,
                1 as threads,
                true as persistent_job,
                jc1.tick as tick
              FROM
                grease.persistant_jobs pj
              INNER JOIN grease.job_config jc1 ON (pj.job_id = jc1.id)
              WHERE
                pj.host_name = %s AND
                pj.enabled = true
            )
            UNION
            (
              SELECT
                jq.id,
                jc.command_module as module,
                jc.command_name as command,
                jq.request_time,
                jq.host_name,
                jq.additional,
                jc.id as command_id,
                jc.is_threaded,
                jc.threads,
                false as persistent_job,
                jc.tick as tick
              FROM
                grease.job_queue jq
              LEFT OUTER JOIN grease.job_config jc ON (jc.id = jq.job_id)
              LEFT OUTER JOIN grease.job_failures jf ON (jf.job_id = jq.id)
              WHERE
                jq.in_progress IS FALSE AND
                jq.completed IS FALSE AND
                jq.host_name = %s AND
                (
                  jf.failures IS NULL OR
                  jf.failures < 5
                )
              ORDER BY
                jq.run_priority desc
              LIMIT
                15
            )
        """
        SQL = self._get_conn().query(SQL, (self._grease_identity, self._grease_identity,))
        # Limit 15 for system stability
        #
        # essentially select all the jobs needing run, flip
        # in_progress to True and return the working array
        #
        normal_jobs = 0
        for job in SQL:
            if str(job['persistent_job']).lower() == 'false':
                self.own_job(job['id'])
                normal_jobs += 1
        self._set_total_normal_jobs(normal_jobs)
        return SQL

    def own_job(self, job_id):
        # type: (int) -> None
        SQL = """
            UPDATE
              grease.job_queue
            SET
              in_progress = true
            WHERE
              id = %s
        """
        self._get_conn().execute(SQL, (job_id,))

    def resolve_job(self, job_id):
        # type: (int) -> None
        SQL = """
            UPDATE
              grease.job_queue
            SET
              in_progress = false,
              completed = true,
              complete_time = current_timestamp
            WHERE
              id = %s
        """
        self._get_conn().execute(SQL, (job_id,))

    def job_failure(self, job_id):
        # type: (int) -> None
        # Add or Increment job_failures table
        sql = """
        INSERT INTO grease.job_failures
            (job_id, failures)
            VALUES
            (%s, 1)
            ON CONFLICT (job_id)
            DO UPDATE SET
            (failures) = (
                (
                    SELECT
                      failures
                    FROM
                      grease.job_failures jf
                    WHERE
                      jf.job_id = %s
                    LIMIT 1
                ) + 1
            )
            WHERE
            job_failures.job_id = %s;
        """
        self._conn.execute(sql, (job_id, job_id, job_id,))
        sql = """
            UPDATE
              grease.job_queue
            SET
              in_progress = false,
              completed = false
            WHERE
              id = %s
        """
        self._get_conn().execute(sql, (job_id,))
