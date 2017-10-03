from tgt_grease_daemon.BaseCommand import GreaseDaemonCommand
from .Article14Section31 import Section31
import os
import uuid
import sys
from tgt_grease_core_util import Configuration
from tgt_grease_core_util import SQLAlchemyConnection
from tgt_grease_core_util.RDBMSTypes import JobServers, ServerHealth, PersistentJobs, JobConfig, JobQueue
from datetime import datetime
from sqlalchemy import update, and_
from tgt_grease_core_util import RDBMSTypes


class LaunchCtl(GreaseDaemonCommand):

    _config = Configuration()
    _sql = SQLAlchemyConnection(_config)

    def __init__(self):
        super(LaunchCtl, self).__init__()
        self.purpose = "Register machine with Job Control Database"

    def execute(self, context='{}'):
        if len(sys.argv) >= 4:
            action = str(sys.argv[3])
        else:
            action = ''
        if action == 'register':
            return bool(self._action_register())
        elif action == 'kill-server':
            return bool(self._action_cull_server())
        elif action == 'revive-server':
            return bool(self._action_restore_server())
        elif action == 'list-pjobs':
            return bool(self._action_list_persistent_jobs())
        elif action == 'list-jobs':
            return bool(self._action_list_job_schedule())
        elif action == 'assign-task':
            return bool(self._action_assign_task())
        elif action == 'remove-task':
            return bool(self._action_remove_task())
        elif action == 'enable-detection':
            return bool(self._action_enable_detection())
        elif action == 'enable-scheduling':
            return bool(self._action_enable_scheduling())
        elif action == 'disable-detection':
            return bool(self._action_disable_detection())
        elif action == 'disable-scheduling':
            return bool(self._action_disable_scheduling())
        elif action == 'create-job':
            return bool(self._action_create_job())
        elif action == 'load-db':
            return bool(self._action_load_db())
        else:
            print("ERR: Invalid Command Expected: ")
            print("\tregister")
            print("\tkill-server")
            print("\trevive-server")
            print("\tlist-pjobs")
            print("\tlist-jobs")
            print("\tassign-task")
            print("\tremove-task")
            print("\tenable-detection")
            print("\tenable-scheduling")
            print("\tdisable-detection")
            print("\tdisable-scheduling")
            print("\tcreate-job")
            print("\tload-db")
            return True

    def _action_register(self):
        # type: () -> bool
        if os.path.isfile(self._config.identity_file):
            self._ioc.message().warning("Machine Already Registered With Grease Job Control")
            print("Machine Already Registered With Grease Job Control")
            return True
        else:
            # we need to register
            # first lets generate a new UUID
            uid = uuid.uuid4()
            # lets see if we have been provided an execution env
            if len(sys.argv) >= 5:
                exe_env = str(sys.argv[4])
            else:
                exe_env = 'general'
            # next lets register with the job control database
            server = JobServers(
                host_name=str(uid),
                execution_environment=exe_env,
                active=True,
                activation_time=datetime.utcnow()
            )
            self._sql.get_session().add(server)
            self._sql.get_session().commit()
            file(self._config.identity_file, 'w').write(str(uid))
            return True

    def _action_cull_server(self):
        # type: () -> bool
        if len(sys.argv) >= 5:
            server = str(sys.argv[4])
        else:
            if os.path.isfile(self._config.identity_file):
                server = self._config.identity
            else:
                print("Server has no registration record locally")
                return True
        # get the server ID
        result = self._sql.get_session().query(JobServers)\
            .filter(JobServers.host_name == server)\
            .first()
        if result:
            server_id = result.id
            instance = Section31()
            instance._declare_doctor(server_id)
            instance._cull_server(server_id)
            return True
        else:
            print("Job Server Not In Registry")
            return True

    def _action_restore_server(self):
        # type: () -> bool
        if len(sys.argv) >= 5:
            server = str(sys.argv[4])
        else:
            if os.path.isfile(self._config.identity_file):
                server = self._config.identity
            else:
                print("Server has no registration record locally")
                return True
        # get the server ID
        result = self._sql.get_session().query(JobServers)\
            .filter(JobServers.host_name == server)\
            .first()
        if result:
            server_id = result.id
        else:
            print("Job Server Not In Registry")
            return True
        # clear the doctor from the server health table
        stmt = update(ServerHealth)\
            .where(ServerHealth.server == server_id)\
            .values(doctor=None)
        self._sql.get_session().execute(stmt)
        self._sql.get_session().commit()
        # next reactivate it
        stmt = update(JobServers)\
            .where(JobServers.id == server_id)\
            .values(active=True, activation_time=datetime.utcnow())
        self._sql.get_session().execute(stmt)
        self._sql.get_session().commit()
        return True

    def _action_list_persistent_jobs(self):
        # type: () -> bool
        result = self._sql.get_session().query(PersistentJobs, JobConfig)\
            .filter(PersistentJobs.command == JobConfig.id)\
            .filter(PersistentJobs.enabled == True)\
            .filter(PersistentJobs.server_id == self._config.node_db_id())\
            .all()
        if not result:
            print("No Scheduled Jobs on this node")
        else:
            for job in result:
                print(
                    "\tPackage: [{0}] Job: [{1}] Tick: [{2}] Additional: [{3}]".format(
                        job.JobConfig.command_module,
                        job.JobConfig.command_name,
                        job.JobConfig.tick,
                        job.PersistentJob.additional
                    )
                )
        return True

    def _action_list_job_schedule(self):
        # type: () -> bool
        result = self._sql.get_session().query(JobQueue)\
            .filter(JobQueue.completed == False)\
            .filter(JobQueue.in_progress == False)\
            .filter(JobQueue.host_name == self._config.node_db_id())\
            .all()
        if not result:
            print("No jobs scheduled on this node")
            return True
        for job in result:
            print("Jobs in Queue:")
            print("\t Module: [{0}] Command: [{1}] Additional: [{2}]".format(
                job.JobConfig.command_module,
                job.JobConfig.command_name,
                job.JobQueue.additional
            ))
        return True

    def _action_assign_task(self):
        # type: () -> bool
        if len(sys.argv) >= 5:
            new_task = str(sys.argv[4])
        else:
            print("Please provide a command to schedule to node")
            return True
        result = self._sql.get_session().query(JobConfig)\
            .filter(JobConfig.command_name == new_task)\
            .first()
        if not result:
            print("Command not found! Available Commands:")
            result = self._sql.get_session().query(JobConfig).all()
            if not result:
                print("NO JOBS CONFIGURED IN DB")
            else:
                for job in result:
                    print("{0}".format(job.command_name))
            return True
        else:
            pJob = PersistentJobs(
                server_id=self._config.node_db_id(),
                command=result.id,
                additional={},
                enabled=True
            )
            self._sql.get_session().add(pJob)
            self._sql.get_session().commit()
            print("TASK ASSIGNED")
            return True

    def _action_remove_task(self):
        # type: () -> bool
        if os.path.isfile(self._config.identity_file):
            server = self._config.node_db_id()
        else:
            print("Server has no registration record locally")
            return True
        if len(sys.argv) >= 5:
            new_task = str(sys.argv[4])
            result = self._sql.get_session().query(JobConfig).filter(JobConfig.command_name == new_task).first()
            if not result:
                print("Failed to find job in configuration tables")
                return True
            else:
                stmt = update(PersistentJobs)\
                    .where(and_(PersistentJobs.server_id == server, PersistentJobs.command == result.id))\
                    .values(enabled=False)
                self._sql.get_session().execute(stmt)
                self._sql.get_session().commit()
                print("TASK UNASSIGNED")
                return True

    def _action_enable_detection(self):
        # type: () -> bool
        if os.path.isfile(self._config.identity_file):
            server = self._config.identity
            stmt = update(JobServers).where(JobServers.host_name == server).values(detector=True)
            self._sql.get_session().execute(stmt)
            self._sql.get_session().commit()
            print("DETECTION ENABLED")
            return True
        else:
            print("ERR: SERVER UNREGISTERED")
            return False

    def _action_enable_scheduling(self):
        # type: () -> bool
        if os.path.isfile(self._config.identity_file):
            server = self._config.identity
            stmt = update(JobServers).where(JobServers.host_name == server).values(scheduler=True)
            self._sql.get_session().execute(stmt)
            self._sql.get_session().commit()
            print("SCHEDULING ENABLED")
            return True
        else:
            print("ERR: SERVER UNREGISTERED")
            return False

    def _action_disable_detection(self):
        # type: () -> bool
        if os.path.isfile(self._config.identity_file):
            server = self._config.identity
            stmt = update(JobServers).where(JobServers.host_name == server).values(detector=False)
            self._sql.get_session().execute(stmt)
            self._sql.get_session().commit()
            print("DETECTION DISABLED")
            return True
        else:
            print("ERR: SERVER UNREGISTERED")
            return False

    def _action_disable_scheduling(self):
        # type: () -> bool
        if os.path.isfile(self._config.identity_file):
            server = self._config.identity
            stmt = update(JobServers).where(JobServers.host_name == server).values(scheduler=False)
            self._sql.get_session().execute(stmt)
            self._sql.get_session().commit()
            print("SCHEDULING DISABLED")
            return True
        else:
            print("ERR: SERVER UNREGISTERED")
            return False

    def _action_create_job(self):
        # type: () -> bool
        if len(sys.argv) >= 6:
            new_task_module = str(sys.argv[4])
            new_task_class = str(sys.argv[5])
            # ensure a job doesn't exist
            result = self._sql.get_session().query(JobConfig)\
                .filter(JobConfig.command_module == new_task_module)\
                .filter(JobConfig.command_name == new_task_class)\
                .all()
            if result:
                print("Job already exists")
                return True
            NewJob = JobConfig(
                command_module=new_task_module,
                command_name=new_task_class
            )
            self._sql.get_session().add(NewJob)
            self._sql.get_session().commit()
            print("Job Created")
            return True
        else:
            print("ERR: INVALID SUBCOMMAND::MUST PASS MODULE AND CLASS NAME")
            return False

    def _action_load_db(self):
        print("LOADING DB")
        RDBMSTypes.__main__()
        return True
