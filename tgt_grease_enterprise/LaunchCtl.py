from tgt_grease_daemon.BaseCommand import GreaseDaemonCommand
from tgt_grease_core_util.Database import Connection
from .Article14Section31 import Section31
from pprint import pprint
import os
import uuid
import sys
from psycopg2 import IntegrityError


class LaunchCtl(GreaseDaemonCommand):
    def __init__(self):
        super(LaunchCtl, self).__init__()
        self.purpose = "Register machine with Job Control Database"
        if os.name == 'nt':
            self._identity_file = "C:\\grease\\grease_identity.txt"
        else:
            self._identity_file = "/tmp/grease/grease_identity.txt"
        self._conn = Connection()

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
            return True

    def _action_register(self):
        # type: () -> bool
        if os.path.isfile(self._identity_file):
            self._ioc.message().warning("Machine Already Registered With Grease Job Control")
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
            sql = """
                INSERT INTO
                  grease.job_servers
                (host_name, execution_environment, activation_time) 
                VALUES 
                (%s, %s, current_timestamp)
            """
            self._conn.execute(sql, (str(uid), exe_env,))
            file(self._identity_file, 'w').write(str(uid))
            return True

    def _action_cull_server(self):
        # type: () -> bool
        if len(sys.argv) >= 5:
            server = str(sys.argv[4])
        else:
            if os.path.isfile(self._identity_file):
                server = file(self._identity_file, 'r').read().rstrip()
            else:
                print("Server has no registration record locally")
                return True
        # get the server ID
        sql = """
            SELECT
              id
            FROM
              grease.job_servers
            WHERE
              host_name = %s
        """
        result = self._conn.query(sql, (server,))
        if len(result) > 0:
            server_id = int(result[0][0])
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
            if os.path.isfile(self._identity_file):
                server = file(self._identity_file, 'r').read().rstrip()
            else:
                print("Server has no registration record locally")
                return True
        # get the server ID
        sql = """
            SELECT
              id
            FROM
              grease.job_servers
            WHERE
              host_name = %s
        """
        result = self._conn.query(sql, (server,))
        if len(result) > 0:
            server_id = int(result[0][0])
        else:
            print("Job Server Not In Registry")
            return True
        # clear the doctor from the server health table
        sql = """
            UPDATE
              grease.server_health
            SET
              doctor = ''
            WHERE
              server_id = %s
        """
        self._conn.execute(sql, (server_id,))
        # next reactivate it
        sql = """
            UPDATE
              grease.job_servers
            SET
              active = TRUE
            WHERE 
              id = %s
        """
        self._conn.execute(sql, (server_id,))
        return True

    def _action_list_persistent_jobs(self):
        # type: () -> bool
        sql = """
            SELECT
              jc.command_module,
              jc.command_name,
              jc.tick,
              pj.additional 
            FROM
              grease.persistant_jobs pj
            INNER JOIN grease.job_config jc ON (jc.id = pj.job_id)
            INNER JOIN grease.job_servers js ON (js.host_name = pj.host_name)
            WHERE
              pj.enabled is true AND 
              js.host_name = %s
        """
        pprint(self._conn.query(sql, (file(self._identity_file, 'r').read().rstrip(),)))
        return True

    def _action_list_job_schedule(self):
        # type: () -> bool
        sql = """
            SELECT
              jq.id,
              jc.command_module,
              jc.command_name,
              jq.additional,
              jq.sn_ticket_number,
              jq.run_priority
            FROM
              grease.job_queue jq
            INNER JOIN grease.job_config jc ON (jc.id = jq.job_id)
            INNER JOIN grease.job_servers js ON (js.host_name = jq.host_name)
            WHERE
              jq.completed is false AND 
              jq.in_progress is false AND
              js.host_name = %s
        """
        pprint(self._conn.query(sql, (file(self._identity_file, 'r').read().rstrip(),)))
        return True

    def _action_assign_task(self):
        # type: () -> bool
        if len(sys.argv) >= 5:
            new_task = str(sys.argv[4])
            if os.path.isfile(self._identity_file):
                server = file(self._identity_file, 'r').read().rstrip()
            else:
                print("Server has no registration record locally")
                return True
            sql = """
                SELECT
                  jc.id
                FROM 
                  grease.job_config jc
                WHERE
                  jc.command_name = %s
            """
            result = self._conn.query(sql, (new_task,))
            if len(result) > 0:
                sql = """
                    INSERT INTO
                      grease.persistant_jobs
                    (host_name, job_id)
                    VALUES 
                    (%s, %s)
                """
                self._conn.execute(sql, (server, result[0][0],))
                print("TASK ASSIGNED")
                return True
            else:
                print("ERR: TASK NOT FOUND IN DATABASE")
                sql = """
                    SELECT
                      jc.command_name
                    FROM 
                      grease.job_config jc
                    ORDER BY 
                      jc.command_module,
                      jc.command_name
                """
                result = self._conn.query(sql)
                print("ERR: AVAILABLE COMMANDS:")
                for row in result:
                    print(" - " + row[0])
                return False
        else:
            print("ERR: NO TASK PROVIDED TO BE ASSIGNED TO THIS SERVER")
            sql = """
                SELECT
                  jc.command_name
                FROM 
                  grease.job_config jc
                ORDER BY 
                  jc.command_module,
                  jc.command_name
            """
            result = self._conn.query(sql)
            print("ERR: AVAILABLE COMMANDS:")
            for row in result:
                    print(" - " + row[0])
            return False

    def _action_remove_task(self):
        # type: () -> bool
        if os.path.isfile(self._identity_file):
            server = file(self._identity_file, 'r').read().rstrip()
        else:
            print("Server has no registration record locally")
            return True
        if len(sys.argv) >= 5:
            new_task = str(sys.argv[4])
            sql = """
                SELECT
                  jc.id
                FROM 
                  grease.job_config jc
                WHERE
                  jc.command_name = %s
            """
            result = self._conn.query(sql, (new_task,))
            if len(result) > 0:
                sql = """
                    UPDATE
                      grease.persistant_jobs
                    SET
                      enabled = FALSE 
                    WHERE
                      host_name = %s
                      AND job_id = %s
                """
                self._conn.execute(sql, (server, result[0][0],))
                print("TASK UNASSIGNED")
                return True
            else:
                print("ERR: TASK NOT FOUND IN DATABASE")
                sql = """
                    SELECT
                      jc.command_name
                    FROM 
                      grease.job_config jc
                    INNER JOIN grease.persistant_jobs pj ON (pj.job_id = jc.id)
                    WHERE
                      pj.host_name = %s 
                      AND pj.enabled is True
                    ORDER BY 
                      jc.command_module,
                      jc.command_name
                """
                result = self._conn.query(sql, (server,))
                print("ERR: AVAILABLE COMMANDS:")
                for row in result:
                    print(" - " + row[0])
                return False
        else:
            print("ERR: NO TASK PROVIDED TO BE ASSIGNED TO THIS SERVER")
            sql = """
                SELECT
                  jc.command_name
                FROM 
                  grease.job_config jc
                INNER JOIN grease.persistant_jobs pj ON (pj.job_id = jc.id)
                WHERE
                  pj.host_name = %s 
                  AND pj.enabled is True
                ORDER BY 
                  jc.command_module,
                  jc.command_name
            """
            result = self._conn.query(sql, (server,))
            print("ERR: AVAILABLE COMMANDS:")
            for row in result:
                    print(" - " + row[0])
            return False

    def _action_enable_detection(self):
        # type: () -> bool
        if os.path.isfile(self._identity_file):
            server = file(self._identity_file, 'r').read().rstrip()
            sql = """
                UPDATE
                  grease.job_servers
                SET
                  detector = TRUE 
                WHERE
                  host_name = %s
            """
            self._conn.execute(sql, (server,))
            print("DETECTION ENABLED")
            return True
        else:
            print("ERR: SERVER UNREGISTERED")
            return False

    def _action_enable_scheduling(self):
        # type: () -> bool
        if os.path.isfile(self._identity_file):
            server = file(self._identity_file, 'r').read().rstrip()
            sql = """
                UPDATE
                  grease.job_servers
                SET
                  scheduler = TRUE 
                WHERE
                  host_name = %s
            """
            self._conn.execute(sql, (server,))
            print("SCHEDULING ENABLED")
            return True
        else:
            print("ERR: SERVER UNREGISTERED")
            return False

    def _action_disable_detection(self):
        # type: () -> bool
        if os.path.isfile(self._identity_file):
            server = file(self._identity_file, 'r').read().rstrip()
            sql = """
                UPDATE
                  grease.job_servers
                SET
                  detector = FALSE 
                WHERE
                  host_name = %s
            """
            self._conn.execute(sql, (server,))
            print("DETECTION DISABLED")
            return True
        else:
            print("ERR: SERVER UNREGISTERED")
            return False

    def _action_disable_scheduling(self):
        # type: () -> bool
        if os.path.isfile(self._identity_file):
            server = file(self._identity_file, 'r').read().rstrip()
            sql = """
                UPDATE
                  grease.job_servers
                SET
                  scheduler = FALSE
                WHERE
                  host_name = %s
            """
            self._conn.execute(sql, (server,))
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
            # get max key
            sql = """
                select max(id) from grease.job_config
            """
            max_id = self._conn.query(sql)
            if len(max_id) > 0:
                max_id = int(max_id[0][0]) + 1
            else:
                max_id = 1
            try:
                sql = """
                    INSERT INTO
                      grease.job_config
                    (id, command_module, command_name) 
                    VALUES 
                    (%s, %s, %s)
                """
                self._conn.execute(sql, (max_id, new_task_module, new_task_class,))
            except IntegrityError:
                print("COMMAND ALREADY ENTERED UNDER THAT NAME")
            return True
        else:
            print("ERR: INVALID SUBCOMMAND::MUST PASS MODULE AND CLASS NAME")
            return False
