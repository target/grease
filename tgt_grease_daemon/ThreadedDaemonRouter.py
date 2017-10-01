from tgt_grease_core import GreaseRouter
from tgt_grease_daemon import GreaseDaemonCommand
from tgt_grease_core_util import Configuration
from tgt_grease_core_util.ImportTools import Importer
from tgt_grease_core_util import Logger
from tgt_grease_core_util.RDBMSTypes import JobQueue, PersistentJobs
from tgt_grease_core_util import SQLAlchemyConnection
from datetime import datetime
from . import Daemon
import os
import sys

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
    _runs = 0
    _throttle_tick = 0
    _job_completed_queue = []
    _current_real_second = datetime.now().second
    _current_run_second = datetime.now().second
    _log = Logger()
    _process = None
    _importer = Importer(_log)
    _job_metadata = {'normal': 0, 'persistent': 0}
    _alchemyConnection = SQLAlchemyConnection(_config)

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
        if len(self.args) <= 2:
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
                    self.have_we_moved_forward_in_time()
                    continue
            # Job Processing
            self.process_queue()
            # Final Clean Up
            self.inc_runs()
            self.inc_throttle_tick()

    def process_queue(self):
        # type: () -> bool
        job_queue = self.get_assigned_jobs()
        if len(job_queue) is 0:
            # have we moved forward since the last second
            if self.have_we_moved_forward_in_time():
                # if we have we can log since the log does not have a record for this second
                self._log.debug("Total Jobs To Process: [0] Current Runs: [{0}]".format(self.get_runs()))
                # We also ensure we record we already logged for zero jobs to process this second
                self.add_job_to_completed_queue(-1)
            else:
                # we have not moved forward in time
                # have we logged for this second
                if not self.has_job_run(-1):
                    # We have not logged for this second so lets do that now
                    self._log.debug("Total Jobs To Process: [0] Current Runs: [{0}]".format(self.get_runs()))
                    # record that we logged for this second
                    self.add_job_to_completed_queue(-1)
        else:
            # We have some jobs to process
            if self._job_metadata['normal'] > 0:
                # if we have any normal jobs lets log
                self._log.debug("Total Jobs To Process: [{0}] Current Runs: [{1}]".format(
                    self._job_metadata['normal'],
                    self.get_runs()
                    )
                )
            else:
                # we only have persistent jobs to process
                # have we moved forward since the last second
                if self.have_we_moved_forward_in_time():
                    # if we have we can log since the log does not have a record for this second
                    self._log.debug("Total Jobs To Process: [{0}] Current Runs: [{1}]".format(
                        len(job_queue),
                        self.get_runs()
                    ))
                    # We also ensure we record we already logged for zero jobs to process this second
                    self.add_job_to_completed_queue(0)
                else:
                    # we have not moved forward in time
                    # have we logged for this second
                    if not self.has_job_run(0):
                        # We have not logged for this second so lets do that now
                        self._log.debug("Total Jobs To Process: [{0}] Current Runs: [{1}]".format(
                            len(job_queue),
                            self.get_runs())
                        )
                        # record that we logged for this second
                        self.add_job_to_completed_queue(0)
            # now lets loop through the job schedule
            for job in job_queue:
                self._log.debug(str(job))
        return True

    def get_assigned_jobs(self):
        """
        gets current job assignment
        :return: list
        """
        # type: () -> list
        return self._alchemyConnection\
            .get_session()\
            .query(JobQueue)\
            .filter(JobQueue.host_name == self._config.node_db_id())

    # Class Property getter/setters/methods

    # run counter
    def get_runs(self):
        """
        returns int of amount of loops
        :return: int
        """
        # type: () -> int
        return int(self._runs)

    def inc_runs(self):
        """
        increments run count
        :return: None
        """
        # type: () -> bool
        self._runs += 1
        return True

    def reset_runs(self):
        """
        resets the run counter to 0
        :return: bool
        """
        # type: () -> bool
        self._runs = 0
        return True

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
        return datetime.now().second

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
