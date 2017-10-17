from tgt_grease_core import GreaseRouter
from tgt_grease_daemon import GreaseDaemonCommand
from tgt_grease_core_util import Configuration
from tgt_grease_core_util import Importer
from tgt_grease_core_util import Logger
from tgt_grease_core_util.RDBMSTypes import JobQueue, PersistentJobs, JobConfig
from tgt_grease_core_util import SQLAlchemyConnection
from sqlalchemy import update, and_, or_
from datetime import datetime
from tgt_grease_core_util import Grease
from psutil import cpu_percent, virtual_memory
from . import Daemon
import threading
import os
import sys
import gc

# PyWin32
if os.name == 'nt':
    import win32event


class DaemonRouter(GreaseRouter.Router):
    """
    Daemon process routing for GREASE
    """
    __author__ = "James E. Bell Jr"
    __version__ = "1.0"

    _config = Configuration()
    _throttle_tick = 0
    _job_completed_queue = []
    _current_real_second = datetime.utcnow().second
    _current_run_second = datetime.utcnow().second
    _log = Logger()
    _process = None
    _importer = Importer(_log)
    _job_metadata = {'normal': 0, 'persistent': 0}
    _alchemyConnection = SQLAlchemyConnection(_config)
    _ioc = Grease()
    _ContextMgr = []

    def __init__(self):
        GreaseRouter.Router.__init__(self)
        if len(self._config.identity) <= 0:
            # ensure we won't run without proper registration
            print("ERR::Unregistered to Database!")
            self._log.error("Registration not found")
            sys.exit(1)

    @staticmethod
    def entry_point():
        """
        Application Entry point
        :return: void
        """
        router = DaemonRouter()
        router.gateway()

    def gateway(self):
        if len(self.args) >= 1:
            if self._config.op_name == 'nt':
                self.set_process(Daemon.WindowsService(sys.argv, self))
            else:
                self.set_process(Daemon.UnixDaemon(self))
            if self.args[0] == 'start':
                self._log.debug("Starting Daemon")
                self.get_process().start()
            elif self.args[0] == 'restart':
                self._log.debug("Restarting Daemon")
                self.get_process().restart()
            elif self.args[0] == 'stop':
                self._log.debug("Stopping Daemon")
                self.get_process().stop()
            else:
                self.bad_exit("Invalid Command To Daemon expected [start,stop,restart]", 2)
        else:
            self.bad_exit("Command not given to daemon! Expected: [start,stop,restart]", 1)

    def main(self):
        """
        Main Daemon Method
        :return: void
        """
        # Job Execution
        self._log.debug("PROCESS STARTUP", True)
        # initial rc value
        rc = "Garbage"
        # All programs are just loops
        while True:
            # Garbage collection
            gc.collect()
            # Windows Signal Catching
            if self._config.op_name == 'nt':
                if not rc != win32event.WAIT_OBJECT_0:
                    self._log.debug("Windows Kill Signal Detected! Closing GREASE")
                    break
            # Continue Processing
            # Process Throttling
            if self._config.get('GREASE_THROTTLE'):
                if int(self.get_throttle_tick()) > int(str(self._config.get('GREASE_THROTTLE'))):
                    # prevent more than 1000 loops per second by default
                    # check time
                    self.log_message_once_a_second("Throttle reached", -11)
                    self.have_we_moved_forward_in_time()
                    continue
            # Job Processing
            if not self._config.get('GREASE_EXECUTE_LINEAR'):
                self.process_queue_threaded()
            else:
                self.log_message_once_a_second("LINEAR EXECUTION MODE DETECTED", -12)
                self.process_queue_standard()
            # Final Clean Up
            self.inc_throttle_tick()
            self.have_we_moved_forward_in_time()
            # After all this check for new windows services
            if os.name == 'nt':
                # Block .5ms to listen for exit sig
                rc = win32event.WaitForSingleObject(self.get_process().hWaitStop, 50)
            # garbage collection
            gc.collect()

    def log_message_once_a_second(self, message, queue_id):
        # type: (str, int) -> bool
        # have we moved forward since the last second
        if self.have_we_moved_forward_in_time():
            # if we have we can log since the log does not have a record for this second
            self._log.debug(message)
            # We also ensure we record we already logged for zero jobs to process this second
            self.add_job_to_completed_queue(queue_id)
            return True
        else:
            # we have not moved forward in time
            # have we logged for this second
            if not self.has_job_run(queue_id):
                # We have not logged for this second so lets do that now
                self._log.debug(message)
                # record that we logged for this second
                self.add_job_to_completed_queue(queue_id)
                return True
            else:
                return False

    def create_obj(self, mod, command):
        # start class up
        command = self._importer.load(mod, command)
        # ensure we got back the correct type
        if not command:
            self._log.error(
                "Failed To Load Command [{0}] of [{1}]"
                .format(
                    command,
                    mod
                ),
                hipchat=True
            )
            del command
            return None
        if not isinstance(command, GreaseDaemonCommand):
            self._log.error("Instance created was not of type GreaseDaemonCommand", hipchat=True)
            del command
            return None
        return command

    def process_queue_standard(self):
        # type: () -> bool
        job_queue = self.get_assigned_jobs()
        if len(job_queue) is 0:
            self.log_message_once_a_second("Total Jobs To Process: [0]", -1)
        else:
            # We have some jobs to process
            if self._job_metadata['normal'] > 0:
                # if we have any normal jobs lets log
                self._log.debug("Total Jobs To Process: [{0}]".format(
                    self._job_metadata['normal']
                )
                )
            else:
                # we only have persistent jobs to process
                self.log_message_once_a_second("Total Jobs To Process: [{0}]".format(
                        len(job_queue)
                    ),
                    0
                )
            # now lets loop through the job schedule
            for job in job_queue:
                # start class up
                command = self._importer.load(job['module'], job['command'])
                # ensure we got back the correct type
                if not command:
                    self._log.error(
                        "Failed To Load Command [{0}] of [{1}]"
                        .format(
                            job['command'],
                            job['module']
                        ),
                        hipchat=True
                    )
                    del command
                    continue
                if not isinstance(command, GreaseDaemonCommand):
                    self._log.error("Instance created was not of type GreaseDaemonCommand", hipchat=True)
                    del command
                    continue
                if not job['persistent']:
                    # This is an on-demand job
                    # we just need to execute it
                    self.mark_job_in_progress(job['id'])
                    self._log.debug("Preparing to execute on-demand job [{0}]".format(job['id']), True)
                    command.attempt_execution(job['id'], job['additional'])
                else:
                    # This is a persistent job
                    if self.has_job_run(job['id']):
                        # Job Already Executed
                        continue
                    else:
                        if job['tick'] is self.get_current_run_second():
                            self._log.debug("Preparing to execute persistent job [{0}]".format(job['id']), True)
                            command.attempt_execution(job['id'], job['additional'])
                            self.add_job_to_completed_queue(job['id'])
                        else:
                            # continue because we are not in the tick required
                            continue
                # Report Telemetry
                self._ioc.run_daemon_telemetry(command)
                if command.get_exe_state()['result']:
                    # job success
                    if job['persistent']:
                        self._log.debug("Persistent Job Successful [{0}]".format(job['id']))
                    else:
                        self._log.debug("On-Demand Job Successful [{0}]".format(job['id']))
                        self.mark_job_complete(job['id'])
                else:
                    # job failed
                    if job['persistent']:
                        self._log.debug("Persistent Job Failed [{0}]".format(job['id']))
                    else:
                        self._log.debug("On-Demand Job Failed [{0}]".format(job['id']))
                        self.mark_job_failure(job['id'], job['failures'])
                command.__del__()
                del command
        return True

    def process_queue_threaded(self):
        # type: () -> bool
        self.thread_check()
        job_queue = self.get_assigned_jobs()
        if len(job_queue) is 0:
            # have we moved forward since the last second
            self.log_message_once_a_second("Total Jobs To Process: [0]", -1)
            del job_queue
            return True
        else:
            # Ensure we aren't swamping the system
            cpu = cpu_percent(interval=1)
            mem = virtual_memory().percent
            if \
                    cpu >= int(self._config.get('GREASE_THREAD_MAX', '85')) \
                    or mem >= int(self._config.get('GREASE_THREAD_MAX', '85')):
                self.log_message_once_a_second(
                    "Thread Maximum Reached CPU: [{0}] Memory: [{1}]".format(cpu, mem),
                    -10
                )
                # remove variables
                del cpu
                del mem
                self.thread_check()
                return True
            # remove variables
            del cpu
            del mem
            # We have some jobs to process
            if self._job_metadata['normal'] is 0:
                # we only have persistent jobs to process
                self.log_message_once_a_second("Total Jobs To Process: [{0}]".format(
                            len(job_queue)
                    ),
                    0
                )
            # now lets loop through the job schedule
            for job in job_queue:
                # check for persistent status
                if not job['persistent']:
                    # This is an on-demand job
                    # we just need to execute it
                    self._log.debug("Passing on-demand job [{0}] to thread manager".format(job['id']), True)
                    command = self.create_obj(job['module'], job['command'])
                    if command:
                        self.thread_execute(command, job['id'], job['additional'], False, job['failures'])
                    else:
                        self._ioc.message().error("Failed to generate command [{0}]".format(job['command']))
                else:
                    # This is a persistent job
                    if self.has_job_run(job['id']):
                        # Job Already Executed
                        continue
                    else:
                        if job['tick'] is self.get_current_run_second():
                            command = self.create_obj(job['module'], job['command'])
                            if command:
                                self.thread_execute(command, job['id'], job['additional'], True)
                            else:
                                self._ioc.message().error("Failed to generate command [{0}]".format(job['command']))
                            self.add_job_to_completed_queue(job['id'])
                        else:
                            # continue because we are not in the tick required
                            continue
        return True

    def thread_execute(self, command, cid, additional, persistent, failures=0):
        # type: (GreaseDaemonCommand, int, dict, bool, int) -> None
        # first ensure the command ID isn't already running
        process_running = False
        for item in self._ContextMgr:
            if item[2] == cid:
                process_running = True
                break
        if process_running:
            # if it is return out
            self._log.debug("Bailing on job [{0}], already executing".format(cid), True)
            return None
        # start process
        proc = threading.Thread(
                target=command.attempt_execution,
                args=(cid, additional),
                name="GREASE EXECUTION THREAD::CID [{0}]".format(cid)
            )
        # set for background
        proc.daemon = True
        if persistent:
            self._log.debug("Beginning persistent execution of job [{0}] on thread".format(cid), True)
        else:
            self.mark_job_in_progress(cid)
            self._log.debug("Beginning on-demand execution of job [{0}] on thread".format(cid))
        # start
        proc.start()
        # add command to pool
        self._ContextMgr.append([
            command,
            proc,
            cid,
            persistent,
            failures
        ])
        return None

    def thread_check(self):
        final = []
        if not len(self._ContextMgr):
            # context manager is empty
            return
        else:
            # Check for tread completion else add back to list
            for command in self._ContextMgr:
                if command[1].isAlive():
                    final.append(command)
                else:
                    self._log.info("Job completed [{0}]".format(command[2]), True)
                    self.record_telemetry(command[0], command[2], command[4], command[3])
            self._ContextMgr = final
        return

    def record_telemetry(self, command, cid, failures, persistent):
        # type: (GreaseDaemonCommand, int, int, bool) -> None
        # Report Telemetry
        command.set_exe_state('command_id', cid)
        self._ioc.run_daemon_telemetry(command)
        if command.get_exe_state()['result']:
            # job success
            if persistent:
                self._log.debug("Persistent Job Successful [{0}]".format(cid))
            else:
                self._log.debug("On-Demand Job Successful [{0}]".format(cid))
                self.mark_job_complete(cid)
        else:
            # job failed
            if persistent:
                self._log.debug("Persistent Job Failed [{0}]".format(cid))
            else:
                self._log.debug("On-Demand Job Failed [{0}]".format(cid))
                self.mark_job_failure(cid, failures)
        command.__del__()
        del command
        pass

    def mark_job_in_progress(self, job_id):
        """
        sets job as in progress
        :param job_id: int
        :return: bool
        """
        stmt = update(JobQueue).where(JobQueue.id == job_id).values(in_progress=True, completed=False)
        self._alchemyConnection.get_session().execute(stmt)
        self._alchemyConnection.get_session().commit()
        return True

    def mark_job_complete(self, job_id):
        """
        Complete a successful job
        :param job_id: int
        :return: bool
        """
        stmt = update(JobQueue)\
            .where(JobQueue.id == job_id)\
            .values(in_progress=False, completed=True, complete_time=datetime.utcnow())
        self._alchemyConnection.get_session().execute(stmt)
        self._alchemyConnection.get_session().commit()
        return True

    def mark_job_failure(self, job_id, current_failures):
        """
        Fail a job
        :param job_id: int
        :param current_failures: int
        :return: bool
        """
        stmt = update(JobQueue)\
            .where(JobQueue.id == job_id)\
            .values(in_progress=False, completed=False, complete_time=None, failures=current_failures + 1)
        self._alchemyConnection.get_session().execute(stmt)
        self._alchemyConnection.get_session().commit()
        return True

    def get_assigned_jobs(self):
        """
        gets current job assignment
        :return: list
        """
        # type: () -> list
        # reset job queue metadata
        self._job_metadata['normal'] = 0
        self._job_metadata['persistent'] = 0
        # create final result
        final = []
        # first find normal jobs
        result = self._alchemyConnection\
            .get_session()\
            .query(JobQueue, JobConfig)\
            .filter(JobQueue.host_name == self._config.node_db_id())\
            .filter(JobQueue.job_id == JobConfig.id) \
            .filter(or_(
                and_(
                        JobQueue.in_progress == False, JobQueue.completed == False
                ),
                JobQueue.in_progress == True)
            ) \
            .filter(JobQueue.failures < 6)\
            .all()
        if not result:
            # No Jobs Found
            self._job_metadata['normal'] = 0
        else:
            # Walk the job list
            for job in result:
                self._job_metadata['normal'] += 1
                final.append({
                    'id': job.JobQueue.id,
                    'module': job.JobConfig.command_module,
                    'command': job.JobConfig.command_name,
                    'request_time': datetime.utcnow(),
                    'additional': job.JobQueue.additional,
                    'tick': job.JobConfig.tick,
                    'persistent': False,
                    'failures': job.JobQueue.failures
                })
        # Now search for persistent jobs
        result = self._alchemyConnection\
            .get_session()\
            .query(PersistentJobs, JobConfig)\
            .filter(PersistentJobs.server_id == self._config.node_db_id())\
            .filter(PersistentJobs.command == JobConfig.id)\
            .filter(PersistentJobs.enabled == True)\
            .all()
        if not result:
            # No Jobs Found
            self._job_metadata['persistent'] = 0
        else:
            # Walk the job list
            for job in result:
                self._job_metadata['persistent'] += 1
                final.append({
                    'id': job.PersistentJobs.id,
                    'module': job.JobConfig.command_module,
                    'command': job.JobConfig.command_name,
                    'request_time': datetime.utcnow(),
                    'additional': job.PersistentJobs.additional,
                    'tick': job.JobConfig.tick,
                    'persistent': True,
                    'failures': 0
                })
        return final

    # Class Property getter/setters/methods

    # Job Completed Queue
    def add_job_to_completed_queue(self, job_ib):
        """
        Adds Job to queue so we don't run the job again
        :param job_ib: int
        :return: bool
        """
        # type: int -> bool
        if int(job_ib) not in self._job_completed_queue:
            self._job_completed_queue.append(int(job_ib))
            return True
        else:
            return False

    def has_job_run(self, job_id):
        """
        Determines if the job ID has run during the current cycle
        :param job_id: int
        :return: bool
        """
        # type: int -> bool
        if int(job_id) in self._job_completed_queue:
            return True
        else:
            return False

    def reset_completed_job_queue(self):
        """
        clears job run queue
        :return: bool
        """
        # type: () -> bool
        self._job_completed_queue = []

    # throttle tick
    def get_throttle_tick(self):
        """
        returns how many runs in this second
        :return: int
        """
        # type: () -> int
        return int(self._throttle_tick)

    def inc_throttle_tick(self):
        """
        increases throttle tick by 1
        :return: bool
        """
        # type: () -> bool
        self._throttle_tick += 1
        return True

    def reset_throttle_tick(self):
        """
        resets throttle tick to 0
        :return: bool
        """
        # type: () -> bool
        self._throttle_tick = 0
        return True

    # Process Controller
    def set_process(self, process):
        """
        sets the process handler
        :param process: Daemon
        :return: None
        """
        self._process = process
        return None

    def get_process(self):
        """
        Returns _process property
        :return: Daemon/None
        """
        return self._process

    # time operators
    @staticmethod
    def get_current_real_second():
        """
        Gets current second
        :return: int
        """
        # type: () -> int
        return datetime.utcnow().second

    def get_current_run_second(self):
        """
        Gets the current observed second
        :return: int
        """
        # type: () -> int
        return int(self._current_run_second)

    def set_current_run_second(self, sec):
        """
        Sets current observed second
        :param sec: int
        :return: None
        """
        # type: int -> None
        self._current_run_second = int(sec)

    def have_we_moved_forward_in_time(self):
        """
        Answers the question "have we moved forward in time?"
        so we reset our counters and return true else false
        :return: bool
        """
        # type: () -> bool
        if self.get_current_run_second() == self.get_current_real_second():
            return False
        else:
            self.set_current_run_second(self.get_current_real_second())
            self.reset_completed_job_queue()
            self.reset_throttle_tick()
            return True
