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
        '_id': ObjectId, # <-- MongoDB ID
        'grease_data': {
            'sourcing': {
                server': ObjectId # <-- Server that performed sourcing
            },
            'detection': {
                server': ObjectId # <-- Server that performed detection
            }
            'scheduling': {
                server': ObjectId # <-- Server that performed scheduling
            }
        },
        'source': String, # <-- Source data came from
        'configuration': String, # <-- Configuration data was sourced for
        'data': dict, # <-- Source data object
        'createTime': DateTime, # <-- DateTime when object was entered into MongoDB **TTL occurs 12 hours after this time**
        'expiry': DateTime, # <-- DateTime when object will expire
        'detectionServer': ObjectId, # <-- MongoDB Object ID of server assigned to perform detection
        'detectionStart': DateTime, # <-- DateTime when detection started
        'detectionEnd': DateTime, # <-- DateTime when detection completed
        'detectionCompleted': Boolean, # <-- True if the detection server is complete with detection on the object
        'schedulingServer': ObjectId, # <-- MongoDB Object ID of server assigned to perform scheduling
        'schedulingStart': DateTime, # <-- DateTime when scheduling started
        'schedulingEnd': DateTime, # <-- DateTime when scheduling completed
        'schedulingCompleted': Boolean, # <-- True if the scheduling server is complete with scheduling for the object
        'schedulingExecutionServer': ObjectId # <-- MongoDB ID of execution server if execution should occur **Only exists for source objects that produce a job**
    }

Data is collected from a source and distributed to each individual dictionary in the collection. Nodes will pick up
each piece of data and process it based on their assignment.
