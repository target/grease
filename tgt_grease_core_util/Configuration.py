import os
from dotenv import load_dotenv
from .RDBMSTypes import JobServers
from .Database import SQLAlchemyConnection


class Configuration(object):
    """
        Handle Node Configuration
    """

    _config = {}
    if os.name == 'nt':
        grease_dir = "C:\\grease"
    else:
        grease_dir = "/var/tmp/grease"
    fs_Separator = os.sep
    op_name = os.name
    grease_log = grease_dir + os.sep + "grease.log"
    identity_file = grease_dir + os.sep + "grease_identity.txt"
    opt_dir = grease_dir + os.sep + "opt" + os.sep
    identity = None
    _node_db_id = None

    def __init__(self):
        # Ensure the GREASE Dir
        if not os.path.isdir(self.grease_dir):
            os.mkdir(self.grease_dir)
        if not os.path.isdir(self.opt_dir):
            os.mkdir(self.opt_dir)
        # load up config
        self._load_config()

    @staticmethod
    def generate():
        # type: () -> Configuration
        return Configuration()

    @staticmethod
    def node_identity():
        # type: () -> str
        if os.path.isfile(Configuration.identity_file):
            fil = open(Configuration.identity_file, "r")
            identity = fil.read().rstrip()
            fil.close()
        else:
            identity = ""
        return identity

    def node_db_id(self):
        # type: () -> int
        if not self._node_db_id:
            identity = Configuration.node_identity()
            conn = SQLAlchemyConnection(Configuration())
            result = conn.get_session().query(JobServers).filter(JobServers.host_name == identity).first()
            self._node_db_id = result.id
        return self._node_db_id

    def get(self, key, default=None):
        # type: (str, str) -> object
        return self._config.get(key, default)

    def _load_config(self):
        # type: () -> None
        # load optional config file
        if os.path.isfile(self.grease_dir + os.sep + "grease.conf"):
            load_dotenv(self.grease_dir + os.sep + "grease.conf", override=True)
        # Load default Environment
        self._config = os.environ
        # Load Identity
        self.identity = self.node_identity()
