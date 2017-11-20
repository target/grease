The GREASE Data Models
***************************

This section covers the different collections of GREASE's MongoDB instance.

The JobServer Collection
==========================

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
===========================

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
                'detectionStart': DateTime, # <-- Time detection server started detection
                'detectionEnd': DateTime, # <-- Time detection server completed detection
                'detection': {} # <-- Data from detection
            },
            'scheduling': { # <-- Scheduling Data
                'schedulingServer': ObjectId, # <-- Server assigned to scheduling
                'schedulingStart': DateTime, # <-- Time scheduling started
                'schedulingEnd': DateTime # <-- Time scheduling completed
            },
            'execution': { # <-- Execution Data
                'server': ObjectId, # <-- Server assigned for execution
                'assignmentTime': DateTime, # <-- Time job was assigned
                'executionStart': DateTime, # <-- Time execution started
                'executionEnd': DateTime, # <-- Time execution ended
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
