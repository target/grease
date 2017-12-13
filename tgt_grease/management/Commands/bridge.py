from tgt_grease.core.Types import Command
from bson.objectid import ObjectId
from bson.errors import InvalidId


class Bridge(Command):
    """CLI tool for cluster administration"""

    __author__ = "James E. Bell Jr."
    __version__ = "2.0.0"
    purpose = "Control node/cluster operations"
    help = """
    CLI for administrators to manage GREASE Clusters
    
    Args:
        register
            register this node with a GREASE Cluster as provided in the configuration file
        info
            --node:<ObjectID>
                Optional parameter to observe a remote node. Defaults to look at self
            --jobs
                if set will list jobs executed
            --pJobs
                include Prototype Jobs in list of jobs
        --foreground
            If set will print log messages to the commandline
    
    """

    def __init__(self):
        super(Bridge, self).__init__()

    def execute(self, context):
        """This method monitors the environment

        An [in]finite loop monitoring the cluster nodes for unhealthy ones

        Args:
            context (dict): context for the command to use

        Returns:
            bool: Command Success

        """
        retVal = False
        if context.get('foreground'):
            self.ioc.getLogger().foreground = True
        if 'register' in context.get('grease_other_args', []):
            retVal = self.action_register()
        elif 'info' in context.get('grease_other_args', []):
            retVal = self.action_info(context.get('node'), context.get('jobs'), context.get('pJobs'))
        else:
            print("Sub-command Not Found! Here is the help information:")
            print(self.help)
            retVal = False
        if context.get('foreground'):
            self.ioc.getLogger().foreground = False
        return retVal

    def action_register(self):
        """Ensures Registration of server

        Returns:
            bool: Registration status

        """
        self.ioc.getLogger().debug("Registration Requested")
        if self.ioc.ensureRegistration():
            print("Registration Complete!")
            self.ioc.getLogger().info("Registration Completed Successfully")
            return True
        else:
            print("Registration Failed!")
            self.ioc.getLogger().info("Registration Failed")
            return False

    def action_info(self, node=None, jobs=None, prototypeJobs=None):
        """Gets Node Information

        Args:
            node (str): MongoDB Object ID to get information about
            jobs (bool): If true then will retrieve jobs executed by this node
            prototypeJobs (bool): If true then prototype jobs will be printed as well

        Note:
            provide a node argument via the CLI --node=4390qwr2fvdew458239
        Note:
            provide a jobs argument via teh CLI --jobs
        Note:
            provide a prototype jobs argument via teh CLI --pJobs

        Returns:
            bool: If Info was found

        """
        if not self.ioc.ensureRegistration():
            self.ioc.getLogger().error("Server not registered with MongoDB")
            print("Unregistered servers cannot talk to the cluster")
            return False
        if node:
            try:
                server = self.ioc.getCollection('JobServer').find_one({'_id': ObjectId(str(node))})
            except InvalidId:
                print("Invalid ObjectID")
                self.ioc.getLogger().error("Invalid ObjectID passed to bridge info [{0}]".format(node))
                return False
            if server:
                serverId = dict(server).get('_id')
            else:
                self.ioc.getLogger().error("Failed to find server [{0}] in the database".format(node))
                return False
        else:
            serverId = self.ioc.getConfig().NodeIdentity
        server = self.ioc.getCollection('JobServer').find_one({'_id': ObjectId(str(serverId))})
        if server:
            server = dict(server)
            print("""
<<<<<<<<<<<<<< SERVER: {0} >>>>>>>>>>>>>>
Activation State: {1} Date: {2}
Jobs: {3}
Operating System: {4}
Prototypes: {5}
Execution Roles: {6}
            """.format(
                server.get('_id'),
                server.get('active'),
                server.get('activationTime'),
                server.get('jobs'),
                server.get('os'),
                server.get('prototypes'),
                server.get('roles'))
            )
            if jobs and prototypeJobs:
                print("======================= SOURCING =======================")
                for job in self.ioc.getCollection('SourceData').find({'grease_data.sourcing.server': ObjectId(serverId)}):
                    print("""
-------------------------------
Job: {0}
-------------------------------
                    """, job['_id'])
            if jobs and prototypeJobs:
                print("======================= DETECTION =======================")
                for job in self.ioc.getCollection('SourceData').find({'grease_data.detection.server': ObjectId(serverId)}):
                    print("""
-------------------------------
Job: {0}
Start Time: {1}
End Time: {2}
Context: {3}
-------------------------------
                    """.format(
                        job['_id'],
                        job['grease_data']['detection']['start'],
                        job['grease_data']['detection']['end'],
                        job['grease_data']['detection']['detection'])
                    )
            if jobs and prototypeJobs:
                print("======================= SCHEDULING =======================")
                for job in self.ioc.getCollection('SourceData').find({'grease_data.scheduling.server': ObjectId(serverId)}):
                    print("""
-------------------------------
Job: {0}
Start Time: {1}
End Time: {2}
-------------------------------
                    """.format(
                        job['_id'],
                        job['grease_data']['scheduling']['start'],
                        job['grease_data']['scheduling']['end'])
                    )
            if jobs:
                print("======================= EXECUTION =======================")
                for job in self.ioc.getCollection('SourceData').find({'grease_data.execution.server': ObjectId(serverId)}):
                    print("""
-------------------------------
Job: {0}
Assignment Time: {1}
Completed Time: {2}
Execution Success: {3}
Command Success: {4}
Failures: {5}
Return Data: {6}
-------------------------------
                    """.format(
                        job['_id'],
                        job['grease_data']['execution']['assignmentTime'],
                        job['grease_data']['execution']['completeTime'],
                        job['grease_data']['execution']['executionSuccess'],
                        job['grease_data']['execution']['commandSuccess'],
                        job['grease_data']['execution']['failures'],
                        job['grease_data']['execution']['returnData'])
                    )
            return True
        else:
            print("Unable to locate server")
            self.ioc.getLogger().error("Unable to load [{0}] server for information".format(serverId))
            return False
