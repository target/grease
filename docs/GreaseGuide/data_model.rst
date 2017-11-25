The GREASE Data Models
***************************

This section covers the different collections of GREASE's MongoDB instance.

Prototype Configurations
===========================

Prototype configurations tell GREASE what to do with data it detects, and where to detect it from. A Typical config
will look like this::

    {
        "name": String, # <-- Unique name for your configuration
        "job": String, # <-- name of command to be run if logic is true
        "exe_env": String, # <-- If not provided will be default as 'general'
        "source": String, # <-- source of data to be provided
        "logic": { # <-- Logical blocks to be evaluated by Detection
            "Regex": [ # <-- example for regex detector
                {
                    "field": String, # <-- field to process
                    "pattern": String # <-- pattern to match
                }
            ]
        }
    }

**NOTE**: This is only an example. See the detection documentation for all the options available to you!

These are stored as JSON files either in the config directory of the project :code:`<PROJECT_ROOT>/tgt_grease/enterprise/Model/config`
or in the GREASE directory in the etc folder :code:`<GREASE_DIR>/etc/` and the file ends with :code:`.config.json`. Another
place to store these configurations is within MongoDB in the :code:`Configuration` collection with the key :code:`type` set
to :code:`prototype_config`.

MongoDB
==========

The JobServer Collection
--------------------------

The JobServer collection is used for data pertaining to Job Servers/Nodes of a GREASE
cluster. A typical record looks like this::

    {
        '_id': ObjectId, # <-- MongoDB ID
        'jobs': Int, # <-- Amount of jobs a node has been assigned
        'os': String, # <-- Operating System of a Node
        'roles': List[String], # <-- Execution Environments a Node will be able to process
        'prototypes': List[String], # <-- Prototypes a Node will run
        'active': Boolean, # <-- Node ready for jobs state
        'activationTime': DateTime # <-- Node activation Time
    }

This is the central registration of a node in GREASE. A node's registration on their
filesystem is the MongoDB ID found in the database.

The SourceData Collection
----------------------------

This collection is responsible for storing all source data. Data is transformed after sourcing traversing through
detection & scheduling eventually making it to the JobQueue collection. This is the primary data model found in this
collection is this:::

    {
        'grease_data': { # <-- Tracing Data for the object moving through the system
            'sourcing': { # <-- Sourcing Data
                'server': ObjectId # <-- Server the source came from
            },
            'detection': { # <-- Detection Data
                'server': ObjectId, # <-- Server assigned to detection
                'start': DateTime, # <-- Time detection server started detection
                'end': DateTime, # <-- Time detection server completed detection
                'detection': Dict # <-- Fields set to be variables in context if any
            },
            'scheduling': { # <-- Scheduling Data
                'server': ObjectId, # <-- Server assigned to scheduling
                'start': DateTime, # <-- Time scheduling started
                'end': DateTime # <-- Time scheduling completed
            },
            'execution': { # <-- Execution Data
                'server': ObjectId, # <-- Server assigned for execution
                'assignmentTime': DateTime, # <-- Time job was assigned
                'start': DateTime, # <-- Time execution started
                'end': DateTime, # <-- Time execution ended
                'context': dict, # <-- Data passed to the command as context
                'executionSuccess': Boolean, # <-- Execution Success
                'commandSuccess': Boolean, # <-- Command Success
                'failures': Int, # <-- Job Execution Failures
                'retryTime': DateTime # <-- If a failure happens, when it should be tried again
            }
        },
        'source': String, # <-- source data came from
        'configuration': String, # <-- Name of configuration data came from
        'data': Dict, # <-- Actual Response Data
        'createTime': DateTime, # <-- Time of Entry
        'expiry': DateTime # <-- Expiration time
    }

Data is collected from a source and distributed to each individual dictionary in the collection. Nodes will pick up
each piece of data and process it based on their assignment.
