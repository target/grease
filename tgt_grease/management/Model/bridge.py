from tgt_grease.core import GreaseContainer
from tgt_grease.core.Types import Command
from bson.objectid import ObjectId
from bson.errors import InvalidId
from tgt_grease.core import ImportTool
from tgt_grease.management.Model import NodeMonitoring
import datetime


class BridgeCommand(object):
    """Methods for Cluster Administration

    Attributes:
        imp (ImportTool): Import Tool Instance
        monitor (NodeMonitoring): Node Monitoring Model Instance

    """

    def __init__(self, ioc=None):
        if isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()
        self.imp = ImportTool(self.ioc.getLogger())
        self.monitor = NodeMonitoring(self.ioc)

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
        valid, serverId = self.valid_server(node)
        if not valid:
            print("Invalid ObjectID")
            return False
        server = self.ioc.getCollection('JobServer').find_one({'_id': ObjectId(str(serverId))})
        if server:
            server = dict(server)
            print(f"""
<<<<<<<<<<<<<< SERVER: {server.get('_id')} >>>>>>>>>>>>>>
Activation State: {server.get('active')} Date: {server.get('activationTime')}
Jobs: {server.get('jobs')}
Operating System: {server.get('os')}
Prototypes: {server.get('prototypes')}
Execution Roles: {server.get('roles')}
            """)
            if jobs and prototypeJobs:
                print("======================= SOURCING =======================")
                for job in self.ioc.getCollection('SourceData').find({'grease_data.sourcing.server': ObjectId(serverId)}):
                    print(f"""
-------------------------------
Job: {job['_id']}
-------------------------------
                    """)
            if jobs and prototypeJobs:
                print("======================= DETECTION =======================")
                for job in self.ioc.getCollection('SourceData').find({'grease_data.detection.server': ObjectId(serverId)}):
                    print(f"""
-------------------------------
Job: {job['_id']}
Start Time: {job['grease_data']['detection']['start']}
End Time: {job['grease_data']['detection']['end']}
Context: {job['grease_data']['detection']['detection']}
-------------------------------
                    """)
            if jobs and prototypeJobs:
                print("======================= SCHEDULING =======================")
                for job in self.ioc.getCollection('SourceData').find({'grease_data.scheduling.server': ObjectId(serverId)}):
                    print(f"""
-------------------------------
Job: {job['_id']}
Start Time: {job['grease_data']['scheduling']['start']}
End Time: {job['grease_data']['scheduling']['end']}
-------------------------------
                    """)
            if jobs:
                print("======================= EXECUTION =======================")
                for job in self.ioc.getCollection('SourceData').find({'grease_data.execution.server': ObjectId(serverId)}):
                    print(f"""
-------------------------------
Job: {job['_id']}
Assignment Time: {job['grease_data']['execution']['assignmentTime']}
Completed Time: {job['grease_data']['execution']['completeTime']}
Execution Success: {job['grease_data']['execution']['executionSuccess']}
Command Success: {job['grease_data']['execution']['commandSuccess']}
Failures: {job['grease_data']['execution']['failures']}
Return Data: {job['grease_data']['execution']['returnData']}
-------------------------------
                    """)
            return True
        print("Unable to locate server")
        self.ioc.getLogger().error(f"Unable to load [{serverId}] server for information")
        return False

    def action_assign(self, prototype=None, role=None, node=None):
        """Assign prototypes/roles to a node either local or remote

        Args:
            prototype (str): Prototype Job to assign
            role (str): Role to assign
            node (str): MongoDB ObjectId of node to assign to, if not provided will default to the local node

        Returns:
            bool: If successful true else false

        """
        assigned = False
        if prototype:
            job = self.imp.load(str(prototype))
            if not job or not isinstance(job, Command):
                print(f"Cannot find prototype [{prototype}] to assign check search path!")
                self.ioc.getLogger().error(f"Cannot find prototype [{prototype}] to assign check search path!")
                return False
            # Cleanup job
            job.__del__()
            del job
            valid, serverId = self.valid_server(node)
            if not valid:
                print("Invalid ObjectID")
                return False
            updated = self.ioc.getCollection('JobServer').update_one(
                {'_id': ObjectId(serverId)},
                {
                    '$addToSet': {
                        'prototypes': prototype
                    }
                }
            ).acknowledged
            if updated:
                print("Prototype Assigned")
                self.ioc.getLogger().info(f"Prototype [{prototype}] assigned to server [{serverId}]")
                assigned = True
            else:
                print("Prototype Assignment Failed!")
                self.ioc.getLogger().info(f"Prototype [{prototype}] assignment failed to server [{serverId}]")
                return False
        if role:
            valid, serverId = self.valid_server(node)
            if not valid:
                print("Invalid ObjectID")
                return False
            updated = self.ioc.getCollection('JobServer').update_one(
                {'_id': ObjectId(serverId)},
                {
                    '$push': {
                        'roles': role
                    }
                }
            ).acknowledged
            if updated:
                print("Role Assigned")
                self.ioc.getLogger().info(f"Role [{prototype}] assigned to server [{serverId}]")
                assigned = True
            else:
                print("Role Assignment Failed!")
                self.ioc.getLogger().info(
                    f"Role [{prototype}] assignment failed to server [{serverId}]")
                return False
        if not assigned:
            print("Assignment failed, please check logs for details")
        return assigned

    def action_unassign(self, prototype=None, role=None, node=None):
        """Unassign prototypes to a node either local or remote

        Args:
            prototype (str): Prototype Job to unassign
            role (str): Role to unassign
            node (str): MongoDB ObjectId of node to unassign to, if not provided will default to the local node

        Returns:
            bool: If successful true else false

        """
        unassigned = False
        if prototype:
            job = self.imp.load(str(prototype))
            if not job or not isinstance(job, Command):
                print(f"Cannot find prototype [{prototype}] to unassign check search path!")
                self.ioc.getLogger().error(f"Cannot find prototype [{prototype}] to unassign check search path!")
                return False
            # Cleanup job
            job.__del__()
            del job
            valid, serverId = self.valid_server(node)
            if not valid:
                print("Invalid ObjectID")
                return False
            updated = self.ioc.getCollection('JobServer').update_one(
                {'_id': ObjectId(serverId)},
                {
                    '$pull': {
                        'prototypes': prototype
                    }
                }
            ).acknowledged
            if updated:
                print("Prototype Assignment Removed")
                self.ioc.getLogger().info(f"Prototype [{prototype}] unassigned from server [{serverId}]")
                unassigned = True
            else:
                print("Prototype Unassignment Failed!")
                self.ioc.getLogger().info(f"Prototype [{prototype}] unassignment failed from server [{serverId}]")
                return False
        if role:
            valid, serverId = self.valid_server(node)
            if not valid:
                print("Invalid ObjectID")
                return False
            updated = self.ioc.getCollection('JobServer').update_one(
                {'_id': ObjectId(serverId)},
                {
                    '$pull': {
                        'roles': role
                    }
                }
            ).acknowledged
            if updated:
                print("Role Removed")
                self.ioc.getLogger().info(f"Role [{prototype}] removed to server [{serverId}]")
                unassigned = True
            else:
                print("Role Removal Failed!")
                self.ioc.getLogger().info(
                    f"Role [{prototype}] removal failed to server [{serverId}]")
                return False
        if not unassigned:
            print("Unassignment failed, please check logs for details")
        return unassigned

    def action_cull(self, node=None):
        """Culls a server from the active cluster

        Args:
            node (str): MongoDB ObjectId to cull; defaults to local node

        """
        if not self.ioc.ensureRegistration():
            self.ioc.getLogger().error("Server not registered with MongoDB")
            print("Unregistered servers cannot talk to the cluster")
            return False
        valid, serverId = self.valid_server(node)
        if not valid:
            print("Invalid ObjectID")
            return False
        if not self.monitor.deactivateServer(serverId):
            self.ioc.getLogger().error(
                f"Failed deactivating server [{serverId}]"
            )
            print(f"Failed deactivating server [{serverId}]")
            return False
        self.ioc.getLogger().warning(
            f"Server [{serverId}] preparing to reallocate detect jobs"
        )
        if not self.monitor.rescheduleDetectJobs(serverId):
            self.ioc.getLogger().error(
                f"Failed rescheduling detect jobs [{serverId}]"
            )
            print(f"Failed rescheduling detect jobs [{serverId}]")
            return False
        self.ioc.getLogger().warning(
            f"Server [{serverId}] preparing to reallocate schedule jobs"
        )
        if not self.monitor.rescheduleScheduleJobs(serverId):
            self.ioc.getLogger().error(
                f"Failed rescheduling detect jobs [{serverId}]"
            )
            print(f"Failed rescheduling detect jobs [{serverId}]")
            return False
        self.ioc.getLogger().warning(
            f"Server [{serverId}] preparing to reallocate jobs"
        )
        if not self.monitor.rescheduleJobs(serverId):
            self.ioc.getLogger().error(
                "Failed rescheduling detect jobs [{serverId}]"
            )
            print(f"Failed rescheduling detect jobs [{serverId}]")
            return False
        print("Server Deactivated")
        return True

    def action_activate(self, node=None):
        """activates server in cluster

        Args:
            node (str): MongoDB ObjectId to activate; defaults to local node

        Returns:
            bool: If activation is successful

        """
        if not self.ioc.ensureRegistration():
            self.ioc.getLogger().error("Server not registered with MongoDB")
            print("Unregistered servers cannot talk to the cluster")
            return False
        valid, serverId = self.valid_server(node)
        if not valid:
            print("Invalid ObjectID")
            return False
        if self.ioc.getCollection('JobServer').update_one(
                {'_id': ObjectId(serverId)},
                {
                    '$set': {
                        'active': True,
                        'activationTime': datetime.datetime.utcnow()
                    }
                }
        ).modified_count < 1:
            self.ioc.getLogger().warning(f"Server [{serverId}] failed to be activated")
            return False
        self.ioc.getLogger().warning(f"Server [{serverId}] activated")
        return True

    def valid_server(self, node=None):
        """Validates node is in the MongoDB instance connected to

        Args:
            node (str): MongoDB Object ID to validate; defaults to local node

        Returns:
            tuple: first element is boolean if valid second is objectId as string

        """
        if node:
            try:
                server = self.ioc.getCollection('JobServer').find_one({'_id': ObjectId(str(node))})
            except InvalidId:
                self.ioc.getLogger().error(f"Invalid ObjectID passed to bridge info [{node}]")
                return False, ""
            if server:
                return True, dict(server).get('_id')
            self.ioc.getLogger().error(f"Failed to find server [{node}] in the database")
            return False, ""
        return True, self.ioc.getConfig().NodeIdentity
