import datetime
from abc import ABCMeta, abstractmethod
from .Database import Connection, SQLAlchemyConnection
from .RDBMSTypes import JobTelemetry, JobTelemetryDaemon
from .Configuration import Configuration
import os


class Telemetry:
    __metaclass__ = ABCMeta

    _config = Configuration()
    _sql = SQLAlchemyConnection(_config)

    def __init__(self, command_obj, is_daemon=False):
        # type: (tgt_grease_core.GreaseCommand, bool) -> None
        self._command = command_obj
        self._is_daemon = is_daemon

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
        telemetry = JobTelemetry(
            command=self._command.get_exe_state().get('command_id', 1),
            success=str(success_state),
            affected=str(self._command.get_effected()),
            start_time=str(datetime.datetime.fromtimestamp(self._command.get_start_time()).strftime('%Y-%m-%d %H:%M:%S')),
            entry_time=datetime.datetime.utcnow(),
            server_id=self._config.node_db_id()
        )
        self._sql.get_session().add(telemetry)
        self._sql.get_session().commit()


class DatabaseDaemon(Telemetry):
    def __init__(self, Command_Obj):
        # type: (tgt_grease_core.GreaseCommand) -> None
        super(DatabaseDaemon, self).__init__(Command_Obj, Command_Obj.get_exe_state()['isDaemon'])

    def store_result(self, success_state=None):
        telemetry = JobTelemetryDaemon(
            command=self._command.get_exe_state()['command_id'],
            affected=self._command.get_effected(),
            start_time=str(datetime.datetime.fromtimestamp(self._command.get_start_time()).strftime('%Y-%m-%d %H:%M:%S')),
            execution_success=self._command.get_exe_state()['execution'],
            command_success=self._command.get_exe_state()['result'],
            entry_time=datetime.datetime.utcnow(),
            server_id=self._config.node_db_id()
        )
        self._sql.get_session().add(telemetry)
        self._sql.get_session().commit()
