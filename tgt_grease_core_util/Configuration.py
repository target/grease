import os
from dotenv import load_dotenv


class Configuration(object):
    """
        Handle Node Configuration
    """

    _config = {}
    if os.name == 'nt':
        grease_dir = "C:\\grease"
    else:
        grease_dir = "/etc/grease"
    fs_Separator = os.sep
    grease_log = grease_dir + os.sep + "grease.log"
    identity_file = grease_dir + os.sep + "grease_identity.txt"
    identity = None

    def __init__(self):
        # Ensure the GREASE Dir
        if not os.path.isdir(self.grease_dir):
            os.mkdir(self.grease_dir)
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
