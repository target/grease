from logging import DEBUG, ERROR, INFO
from tgt_grease.core import GreaseContainer, ImportTool
from tgt_grease.core.Types import Command
from tgt_grease.enterprise.Model import PrototypeConfig
from datetime import datetime
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
        conf (PrototypeConfig): Prototype Configuration Instance

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
        self.conf = PrototypeConfig(self.ioc)

    def server(self):
        """Server process for ensuring prototypes & jobs are running

        By Running this method this will clear the DB of any jobs a node may have

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
        JobsCollection = self.ioc.getCollection("SourceData")
        self.ioc.getLogger().trace("Searching for Jobs", trace=True)
        jobs = JobsCollection.find({
            'grease_data.execution.server': ObjectId(self.ioc.getConfig().NodeIdentity),
            'grease_data.execution.commandSuccess': False,
            'grease_data.execution.executionSuccess': False,
            'grease_data.execution.failures': {'$lt': 6}
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
                self._run_job(job, JobsCollection)
        else:
            # Nothing to Run for Jobs
            self.ioc.getLogger().trace("No Jobs Scheduled to Server", trace=True)
        self.ioc.getLogger().trace("Server execution complete", trace=True)
        return True

    def _run_job(self, job, JobCollection):
        """Run a On-Demand Job

        Args:
            job (dict): Job Data to execute
            JobCollection (pymongo.collection.Collection): JobCollection to update for telemetry

        Returns:
            None: Void Method to kickoff execution

        """
        if not self.contextManager['jobs'].get(job.get('_id')):
            # New Job to run
            if isinstance(job.get('configuration'), bytes):
                conf = job.get('configuration').decode()
            else:
                conf = job.get('configuration')
            inst = self.impTool.load(self.conf.get_config(conf).get('job'))
            if inst and isinstance(inst, Command):
                inst.ioc.getLogger().foreground = self.ioc.getLogger().foreground
                thread = threading.Thread(
                    target=inst.safe_execute,
                    args=(job.get('grease_data', {}).get('detection', {}).get('detection', {}),),
                    name="GREASE DAEMON COMMAND EXECUTION [{0}]".format(job.get('_id'))
                )
                thread.daemon = True
                thread.start()
                self.contextManager['jobs'][job.get("_id")] = {
                    'thread': thread,
                    'command': inst
                }
            else:
                # Invalid Job
                del inst
                self.ioc.getLogger().warning("Invalid Job", additional=job)
                JobCollection.update_one(
                    {'_id': ObjectId(job['_id'])},
                    {
                        '$set': {
                            'grease_data.execution.failures': job.get('failures', 0) + 1
                        }
                    }
                )
            return
        else:
            # Job already executing
            if self.contextManager['jobs'].get(job.get('_id')).get('thread').isAlive():
                # thread still executing
                return
            else:
                # Execution has ended
                self.ioc.getLogger().trace("Job [{0}] finished running".format(job.get('_id')), trace=True)
                finishedJob = self.contextManager['jobs'].get(job.get('_id')).get('command')  # type: Command
                if finishedJob.getRetVal():
                    # job completed successfully
                    JobCollection.update_one(
                        {'_id': ObjectId(job.get('_id'))},
                        {
                            '$set': {
                                'grease_data.execution.commandSuccess': finishedJob.getRetVal(),
                                'grease_data.execution.executionSuccess': finishedJob.getExecVal(),
                                'grease_data.execution.completeTime': datetime.utcnow(),
                                'grease_data.execution.returnData': finishedJob.getData()
                            }
                        }
                    )
                else:
                    # Job Failure
                    self.ioc.getLogger().warning(
                        "Job Failed [{0}]".format(job.get('_id')), additional=finishedJob.getData()
                    )
                    # TODO: Job Execution cooldown timing
                    JobCollection.update_one(
                        {'_id': ObjectId(job['_id'])},
                        {
                            '$set': {
                                'grease_data.execution.failures': job.get('grease_data', {}).get('execution', {}).get('failures', 0) + 1
                            }
                        }
                    )
                # close out job
                finishedJob.__del__()
                del finishedJob
                # remove from contextManager
                del self.contextManager['jobs'][job.get('_id')]
                return

    def _run_prototype(self, prototype):
        """Startup a ProtoType

        Args:
            prototype (str): ProtoType to start

        Returns:
            None: Void method to start prototype

        """
        if not self.contextManager['prototypes'].get(prototype):
            # ProtoType has not started
            inst = self.impTool.load(prototype)
            if not isinstance(inst, Command):
                # invalid ProtoType
                self.log_once_per_second("Invalid ProtoType [{0}]".format(prototype), level=ERROR)
                return
            inst.ioc.getLogger().foreground = self.ioc.getLogger().foreground
            thread = threading.Thread(
                target=inst.safe_execute,
                args=({}),
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

    def drain_jobs(self, JobCollection):
        """Will drain jobs from the current context

        This method is used to prevent abnormal ending of executions

        Args:
            JobCollection (pymongo.collection.Collection): Job Collection Object

        Returns:
            bool: When job queue is emptied

        """
        Threads = True
        while Threads:
            if self.contextManager['jobs']:
                jobs = {}
                for key, val in self.contextManager['jobs'].items():
                    if val['thread'].isAlive():
                        jobs[key] = val
                        continue
                    else:
                        # Execution has ended
                        self.ioc.getLogger().trace("Job [{0}] finished running".format(key), trace=True)
                        finishedJob = self.contextManager['jobs'].get(key).get('command')  # type: Command
                        if finishedJob.getRetVal():
                            # job completed successfully
                            JobCollection.update_one(
                                {'_id': ObjectId(key)},
                                {
                                    '$set': {
                                        'grease_data.execution.commandSuccess': finishedJob.getRetVal(),
                                        'grease_data.execution.executionSuccess': finishedJob.getExecVal(),
                                        'grease_data.execution.completeTime': datetime.utcnow(),
                                        'grease_data.execution.returnData': finishedJob.getData()
                                    }
                                }
                            )
                        else:
                            # Job Failure
                            self.ioc.getLogger().warning(
                                "Job Failed [{0}]".format(key), additional=finishedJob.getData()
                            )
                            JobCollection.update_one(
                                {'_id': ObjectId(key)},
                                {
                                    '$set': {
                                        'grease_data.execution.failures': val['command'].get('failures', 0) + 1
                                    }
                                }
                            )
                        # close out job
                        finishedJob.__del__()
                        del finishedJob
                self.contextManager['jobs'] = jobs
            else:
                Threads = False
        return True

    def register(self):
        """Attempt to register with MongoDB

        Returns:
            bool: Registration Success

        """
        return self.ioc.ensureRegistration()

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
