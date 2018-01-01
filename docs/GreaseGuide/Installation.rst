.. _installing-grease:

GREASE Up & Running
****************************

Initial Installation
=======================

Via PyPi: The Traditional Way
---------------------------------

GREASE is built like any other traditional python software, as a package. This means many things but luckily for
the systems administrator it means we traverse the typical PyPi pipeline allowing for you to specify your version
and allow for updates to be pretty easy. Here is the installation steps:

#. Run `pip install tgt_grease`
#. Setup your configuration file following

From Source on GitHub: Because you're cool like that
-------------------------------------------------------

GREASE is developer friendly! We're always looking for new ways to bring joy to our guests as well as our developers. To
install GREASE via source follow these steps:

#. Download the repo either via Git or HTTP from GitHub
#. Enter the project folder you created
#. Run `python setup.py install`

   - **NOTE:** We recommend for all use cases to use a virtual environment

#. Setup your configuration file

Understanding the configuration System
========================================

There are multiple definitions for configuration in GREASE. The primary ones are:

#. Node Configuration: This refers to the local server's configuration for things like MongoDB credentials & resource limits
#. Cluster Configuration: This refers to the configuration of Job Servers inside of the cluster
#. Prototype Configuration: These are the configurations for prototypes, things such as sourcing & detection

Node Configuration
----------------------

.. _nodeconfig:

Node configuration is the local file the running instance uses to execute GREASE operations. The default configuration
looks like this::

    {
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

Lets go through each key and the properties below, what they control and some values you may want to use.

* Connectivity: This is the store for details around connectivity
    * MongoDB: This key is the key used to find connection details about the central database

        =========== =============   ============
        Key         value type      default
        =========== =============   ============
        host        str             localhost
        port        int             27017
        username    str
        password    str
        db          str
        =========== =============   ============
* Logging: Logging configuration information
    * mode: only supports filesystem logging currently to the log file
    * verbose: Can either be True or False. Setting it to True would print any message where the verbose flag was passed. Note, the only internal system of GREASE that utilizes verbose is deduplication. The rest is in tracing
    * trace: Can either be True or False. This enables tracing from within GREASE. This will show a "stream of consciousness" in the log files.
    * foreground: Can either be True or False. True would print log messages to stdout as well as a log file
    * file: Log file to write messages to
* Notifications: Stores information about notification channels. All channels will need at least one key, "enabled" with a boolean True/False value to enable or disable the channel. All other keys are dependent on the notification channel
* Configuration: This section contains information about this node's prototype configurations
    * dir: A directory string on where to load configurations from
* Sourcing: This section contains information about this node's sourcing prototype configuration
    * dir: A directory string on where to load configurations from
    * source: A string defaulted to null that if provided sourcing will focus only on prototype configurations from that source to get source data from
    * config: A string defaulted to null that if provided sourcing will focus only that prototype configuration
    * mock: A boolean value which when enabled will attempt to source mocking data dependent from the prototype configurations
* Import: This section holds information about the import system
    * searchPath: A list of strings of packages to attempt loading commands from
* NodeInformation: This section controls how GREASE performs on the Node
    * ResourceMax: Integer that GREASE uses to ensure that new jobs or processes are not spun up if *memory or CPU* utilization exceed this limit
    * DeduplicationThreads: This integer is how many threads to keep open at one time during deduplication. On even the largest source data sets the normal open threads is 30 but this provides a safe limit at 150 by default
* Additional: Unused currently but can be used for additional user provided configuration

Cluster Configuration
-----------------------

Cluster configuration is stored in the MongoDB collection JobServer. Check the :ref:`datamodel` for more information
about what is stored here.

Prototype Configuration
------------------------

Prototype configuration is stored in the MongoDB collection Configuration, in the filesystem or located in the package.
Check the :ref:`datamodel` for more information about what is stored here and the schema.
