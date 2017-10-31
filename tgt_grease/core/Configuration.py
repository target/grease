import os
import json

##
# Global Configuration Object
##
GREASE_CONFIG = None


class Configuration(object):
    """GREASE Configuration Management

    This class is responsible for management of configuration of a GREASE Node. Default Configuration will be
    used if the grease.conf.json document is not found in the root of the GREASE directory. It will ensure all
    folders/files are in the directory and serve as the access point for configuration data

    Attributes:
        greaseDir (str): The root directory of GREASE
        fs_sep (str): The filesystem separator for the installed OS
        greaseConfigFile (str): Location of the current configuration file
        FileSystem (list): Directories of the GREASE filesystem
        GREASE_CONFIG (dict): Actual config

    """
    global GREASE_CONFIG

    if os.environ.get('GREASE_DIR'):
        greaseDir = os.environ.get('GREASE_DIR')
    else:
        if os.name == 'nt':
            greaseDir = "C:\\grease\\"
        else:
            greaseDir = "/opt/grease/"

    FileSystem = ['etc', 'log']

    fs_sep = os.sep

    greaseConfigFile = greaseDir + "grease.conf.json"

    def __init__(self, ConfigFile=None):
        self.EnsureGreaseFS()
        self.ReloadConfig(ConfigFile)

    @staticmethod
    def ReloadConfig(ConfigFile=None):
        """[Re]loads the configuration

        Returns:
            None: Void Method

        """
        global GREASE_CONFIG
        if ConfigFile:
            Configuration.greaseConfigFile = ConfigFile
        if os.path.isfile(Configuration.greaseConfigFile):
            # attempt loading
            try:
                fil = open(Configuration.greaseConfigFile)
                GREASE_CONFIG = json.loads(fil.read())
                fil.close()
            except:
                # load defaults
                GREASE_CONFIG = Configuration.DefaultConfig()
        else:
            # load defaults
            GREASE_CONFIG = Configuration.DefaultConfig()
            # write config to disk
            fil = open(Configuration.greaseConfigFile, 'w')
            fil.write(json.dumps(GREASE_CONFIG))
            fil.close()

    @staticmethod
    def get(section, key):
        """Retrieve configuration item

        Args:
            section (str): Configuration Section to read from
            key (str): Configuration key to retrieve

        """
        global GREASE_CONFIG
        if isinstance(GREASE_CONFIG, dict):
            if GREASE_CONFIG.get(section):
                if isinstance(GREASE_CONFIG.get(section), dict) and key in GREASE_CONFIG.get(section):
                    return GREASE_CONFIG.get(section).get(key)
                else:
                    return None
            else:
                return None
        else:
            return False

    #########
    # Initialization / Internal Methods
    #########

    def EnsureGreaseFS(self):
        """Ensures the GREASE Directory structure is setup

        Returns:
            bool: If the FS is in place then True

        """
        if not os.path.isdir(self.greaseDir):
            os.mkdir(self.greaseDir)
        for elem in self.FileSystem:
            if not os.path.isdir(self.greaseDir + os.sep + elem):
                os.mkdir(self.greaseDir + os.sep + elem)
        return True

    @staticmethod
    def DefaultConfig():
        """Returns the Default GREASE Config

        Returns:
            dict: Default Configuration

        """
        return {
            'Connectivity': {
                'MongoDB': {
                    'host': 'localhost',
                    'port': 27017
                }
            },
            'Logging': {
                'mode': 'filesystem',
                'verbose': False,
                'trace': False,
                'foreground': False,
                'file': Configuration.greaseDir + os.sep + 'log' + os.sep + 'grease.log'
            },
            'Configuration': {
                'mode': 'filesystem',
                'dir': Configuration.greaseDir + os.sep + 'etc'
            },
            'Sourcing': {
                'mode': 'filesystem',
                'dir': Configuration.greaseDir + os.sep + 'etc'
            },
            "Additional": {}
        }
