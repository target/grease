import datetime
from abc import ABCMeta, abstractmethod
from .Database import Connection
import os


class Telemetry:
    __metaclass__ = ABCMeta

    def __init__(self, command_obj, is_daemon=False):
        # type: (tgt_grease_core.GreaseCommand, bool) -> None
        self._command = command_obj
        self._is_daemon = is_daemon
        self._conn = Connection.create()
        if os.name == 'nt':
            self._identity_file = "C:\grease\grease_identity.txt"
        else:
            self._identity_file = "/tmp/grease/grease_identity.txt"
        if os.path.isfile(self._identity_file):
            self._grease_identity = str(open(self._identity_file, 'r').read()).rstrip()
        else:
            self._grease_identity = ''

    @abstractmethod
    def store_result(self, success_state):
        # type: (bool) -> None
        pass


class Database(Telemetry):
    def __init__(self, command_obj, is_daemon):
        # type: (tgt_grease_core.GreaseCommand, bool) -> None
        Telemetry.__init__(self, command_obj, is_daemon)

    def store_result(self, success_state):
        # type: () -> None
        if self._is_daemon:
            sql = """
            INSERT INTO
               grease.job_telemetry
            (command, success, effected, start_time, is_daemon, server_id)
            VALUES
            (%s, %s, %s, %s, %s, %s)
        """
            params = (
                str(type(self._command).__name__),
                str(success_state),
                str(self._command.get_effected()),
                str(datetime.datetime.fromtimestamp(self._command.get_start_time()).strftime('%Y-%m-%d %H:%M:%S')),
                'true',
                str(self._grease_identity)
            )
        else:
            sql = """
                    INSERT INTO
                       grease.job_telemetry
                    (command, success, effected, start_time, server_id)
                    VALUES
                    (%s, %s, %s, %s, %s)
                """
            params = (
                str(type(self._command).__name__),
                str(success_state),
                str(self._command.get_effected()),
                str(datetime.datetime.fromtimestamp(self._command.get_start_time()).strftime('%Y-%m-%d %H:%M:%S')),
                self._grease_identity
            )
        self._conn.execute(sql, params)


class DatabaseDaemon(Telemetry):
    def __init__(self, Command_Obj):
        # type: (tgt_grease_core.GreaseCommand) -> None
        super(DatabaseDaemon, self).__init__(Command_Obj, Command_Obj.get_exe_state()['isDaemon'])

    def store_result(self, success_state=None):
        sql = """
            INSERT INTO
              grease.job_telemetry_daemon
            (command_id, class_name, execution_success, command_success, effected, start_time, server_id)
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """
        params = (
            self._command.get_exe_state()['command_id'],
            str(type(self._command).__name__),
            self._command.get_exe_state()['execution'],
            self._command.get_exe_state()['result'],
            self._command.get_effected(),
            str(datetime.datetime.fromtimestamp(self._command.get_start_time()).strftime('%Y-%m-%d %H:%M:%S')),
            self._grease_identity,
        )
        self._conn.execute(sql, params)
