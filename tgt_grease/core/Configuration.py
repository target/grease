import os
import json

##
# Global Configuration Object
##
GREASE_CONFIG = {}


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

    if os.path.isfile(greaseDir + 'grease.identity'):
        with open(greaseDir + 'grease.identity', 'r') as fil:
            NodeIdentity = fil.read().rstrip()
    else:
        NodeIdentity = "Unknown"

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
            try:
                with open(Configuration.greaseConfigFile, 'w') as fil:
                    fil.write(json.dumps(GREASE_CONFIG, indent=4, sort_keys=True))
            except:
                print("""
!!!!!!!!!!!!!!!!!!FAILED TO WRITE CONFIGURATION!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                
THIS IS CRITICAL! EITHER [{0}] is unavailable or does not exist! log files will not be written and only the
default configuration is accessible!

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                """.format(Configuration.greaseDir))
                return

    @staticmethod
    def get(section, key=None, default=None):
        """Retrieve configuration item

        Args:
            section (str): Configuration Section to read from
            key (str): Configuration key to retrieve
            default (object): Default value if section/key is not found

        """
        global GREASE_CONFIG
        if isinstance(GREASE_CONFIG, dict):
            if GREASE_CONFIG.get(section):
                if key:
                    if isinstance(GREASE_CONFIG.get(section), dict) and key in GREASE_CONFIG.get(section):
                        return GREASE_CONFIG.get(section).get(key)
                    else:
                        return default
                else:
                    return GREASE_CONFIG.get(section)
            else:
                return default
        else:
            return False

    def set(self, key, value, section=None):
        """Set configuration item

        Args:
            section (str): Configuration Section to set
            key (str): Configuration key to set
            value (object): value to set

        Returns:
            None: Sets item only

        """
        global GREASE_CONFIG
        if section:
            if isinstance(GREASE_CONFIG, dict):
                if GREASE_CONFIG.get(section):
                    GREASE_CONFIG[section][key] = value
                else:
                    GREASE_CONFIG[section] = dict()
                    GREASE_CONFIG[section][key] = value
            else:
                return False
        else:
            GREASE_CONFIG[key] = value

    #########
    # Initialization / Internal Methods
    #########

    def EnsureGreaseFS(self):
        """Ensures the GREASE Directory structure is setup

        Returns:
            bool: If the FS is in place then True

        """
        try:
            if not os.path.isdir(self.greaseDir):
                os.mkdir(self.greaseDir)
            for elem in self.FileSystem:
                if not os.path.isdir(self.greaseDir + elem):
                    os.mkdir(self.greaseDir + elem)
            return True
        except:
            return False

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
                'file': Configuration.greaseDir + 'log' + os.sep + 'grease.log'
            },
            'Notifications': {
                'HipChat': {
                    'enabled': False,
                    'token': None,
                    'room': None
                },
                'Slack': {
                    'enabled': False,
                    'webhookURL': ''
                }
            },
            'Configuration': {
                'dir': Configuration.greaseDir + 'etc' + os.sep
            },
            'Sourcing': {
                'dir': Configuration.greaseDir + 'etc' + os.sep,
                'source': None,
                'config': None,
                'mock': False
            },
            'Import': {
                'searchPath': [
                    'tgt_grease.router.Commands',
                    'tgt_grease.enterprise.Prototype',
                    'tgt_grease.management.Commands',
                    'tgt_grease.enterprise.Sources',
                    'tgt_grease.enterprise.Detectors',
                    'tgt_grease.core',
                    'tgt_grease'
                ]
            },
            "NodeInformation": {
                "ResourceMax": 95,
                "DeduplicationThreads": 150
            },
            "Additional": {}
        }
