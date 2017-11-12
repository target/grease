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
