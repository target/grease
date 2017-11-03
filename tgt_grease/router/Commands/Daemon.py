from logging import DEBUG, ERROR, INFO
from tgt_grease.core import GreaseContainer, ImportTool
from tgt_grease.core.Types import Command
from datetime import datetime
import platform
from bson.objectid import ObjectId
import threading
from psutil import cpu_percent, virtual_memory


class DaemonProcess(object):
    """Actual daemon processing for GREASE Daemon

    Attributes:
        ioc (GreaseContainer): The Grease IOC
        current_real_second (int): Current second in time
        registered (bool): If the node is registered with MongoDB
        impTool (ImportTool): Instance of Import Tool

    """

    ioc = None
    current_real_second = None
    registered = True
    contextManager = {'jobs': {}, 'prototypes': {}}
    impTool = None

    def __init__(self, ioc):
        if isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()
        self.current_real_second = datetime.utcnow().second
        if self.ioc.getConfig().NodeIdentity == "Unknown" and not self.register():
            self.registered = False
        self.impTool = ImportTool(self.ioc.getLogger())

    def server(self):
        """Server process for ensuring prototypes & jobs are running

        Returns:
            bool: Server Success

        """
        # Ensure we aren't swamping the system
        cpu = cpu_percent(interval=.1)
        mem = virtual_memory().percent
        if \
                cpu >= int(self.ioc.getConfig().get('NodeInformation', 'ResourceMax')) \
                or mem >= int(self.ioc.getConfig().get('NodeInformation', 'ResourceMax')):
            self.ioc.getLogger().trace(
                "Thread Maximum Reached CPU: [{0}] Memory: [{1}]".format(cpu, mem),
                trace=True
            )
            # remove variables
            del cpu
            del mem
            return True
        if not self.registered:
            self.ioc.getLogger().trace("Server is not registered", trace=True)
            return False
        self.ioc.getLogger().trace("Server execution starting", trace=True)
        # establish job collection
        JobsCollection = self.ioc.getCollection("JobQueue")
        self.ioc.getLogger().trace("Searching for Jobs", trace=True)
        jobs = JobsCollection.find({
            'node': ObjectId(self.ioc.getConfig().NodeIdentity),
            'completed': False
        })
        # Get Node Information
        Node = self.ioc.getCollection('JobServer').find_one({'_id': ObjectId(self.ioc.getConfig().NodeIdentity)})
        if not Node:
            # If for some reason we couldn't find it
            self.ioc.getLogger().error("Failed To Load Node Information")
            return False
        # Get Prototypes
        prototypes = list(Node.get('prototypes'))
        # Del node instance
        del Node
        if prototypes:
            # We have prototypes to spin up
            for prototype in prototypes:
                self.ioc.getLogger().trace("Passing ProtoType [{0}] to Runner".format(prototype), trace=True)
                self._run_prototype(prototype)
        if jobs.count():
            self.ioc.getLogger().trace("Total Jobs to Execute: [{0}]".format(jobs.count()))
            for job in jobs:
                self.ioc.getLogger().trace("Passing Job [{0}] to Runner".format(job.get("_id")), trace=True)
                self._run_job(job)
        else:
            # Nothing to Run for Jobs
            self.ioc.getLogger().trace("No Jobs Scheduled to Server", trace=True)
        self.ioc.getLogger().trace("Server execution complete", trace=True)
        return True

    def _run_job(self, job):
        # TODO: Ensure Job not already in progress
        pass

    def _run_prototype(self, prototype):
        if not self.contextManager['prototypes'].get(prototype):
            # ProtoType has not started
            inst = self.impTool.load(prototype)
            if not isinstance(inst, Command):
                # invalid ProtoType
                self.log_once_per_second("Invalid ProtoType [{0}]".format(prototype), level=ERROR)
                return
            inst.ioc.getLogger().foreground = self.ioc.getLogger().foreground
            thread = threading.Thread(
                target=inst.execute,
                name="GREASE DAEMON PROTOTYPE [{0}]".format(prototype)
            )
            thread.daemon = True
            thread.start()
            self.contextManager['prototypes'][prototype] = thread
            return
        else:
            # ensure thread is alive
            if self.contextManager['prototypes'].get(prototype).isAlive():
                self.ioc.getLogger().trace("ProtoType [{0}] is alive".format(prototype))
                return
            else:
                # Thread died for some reason
                self.log_once_per_second("ProtoType [{0}] Stopped".format(prototype), level=INFO)
                inst = self.impTool.load(prototype)
                if not isinstance(inst, Command):
                    self.log_once_per_second("Invalid ProtoType [{0}]".format(prototype), level=ERROR)
                    return
                inst.ioc.getLogger().foreground = self.ioc.getLogger().foreground
                thread = threading.Thread(
                    target=inst.execute,
                    name="GREASE DAEMON PROTOTYPE [{0}]".format(prototype)
                )
                thread.daemon = True
                thread.start()
                self.contextManager['prototypes'][prototype] = thread
                return

    def register(self):
        """Attempt to register with MongoDB

        Returns:
            bool: Registration Success

        """
        # TODO: Make a cluster management command to utilize this in more places
        collection = self.ioc.getCollection("JobServer")
        if self.ioc.getConfig().NodeIdentity == "Unknown":
            # Actual registration
            uid = collection.insert_one({
                'jobs': 0,
                'os': platform.system().lower(),
                'roles': self.ioc.getConfig().get('NodeInformation', "Roles"),
                'prototypes': self.ioc.getConfig().get('NodeInformation', "ProtoTypes"),
                'active': True,
                'activationTime': datetime.utcnow()
            }).inserted_id
            fil = open(self.ioc.getConfig().greaseDir + "grease.identity", "w")
            fil.write(str(uid))
            fil.close()
            self.registered = True
            self.ioc.getConfig().NodeIdentity = uid
            del collection
            return True
        else:
            # Check the Identity is actually registered
            if collection.find({'_id': ObjectId(self.ioc.getConfig().NodeIdentity)}).count():
                del collection
                return True
            else:
                self.ioc.getLogger().error("Invalid Node Identity::Node Identity Not Found", additional={
                    'NodeID': self.ioc.getConfig().NodeIdentity
                })
                del collection
                return False

    def log_once_per_second(self, message, level=DEBUG, additional=None):
        """Log Message once per second

        Args:
            message (str): Message to log
            level (int): Log Level
            additional (object): Additional information that is able to be str'd

        Returns:
            None: Void Method to fire log message

        """
        if self._has_time_progressed():
            self.ioc.getLogger().TriageMessage(message=message, level=level, additional=additional)

    def _has_time_progressed(self):
        """Determines if the current second and the real second are not the same

        Returns:
            bool: if true then time has passed in a meaningful way

        """
        if self.current_real_second != datetime.utcnow().second:
            self.current_real_second = datetime.utcnow().second
            return True
        else:
            return False
