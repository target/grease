from tgt_grease.core import GreaseContainer
from tgt_grease.enterprise.Model import Scheduling
from tgt_grease.enterprise.Model import Scheduler
from tgt_grease.enterprise.Model import Deduplication
from bson.objectid import ObjectId
import datetime


class NodeMonitoring(object):
    """Monitors cluster nodes for unhealthy state

    Attributes:
        ioc (GreaseContainer): IoC Access
        centralScheduler (Scheduling): Central Scheduling Instance
        scheduler (Scheduler): Scheduling Model Instance

    """

    def __init__(self, ioc=None):
        if isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()
        self.centralScheduler = Scheduling(self.ioc)
        self.scheduler = Scheduler(self.ioc)

    def monitor(self):
        """Monitoring process

        Returns:
            bool: If successful monitoring run occurred

        """
        servers = self.getServers()
        retVal = False
        self.ioc.getLogger().debug("Total servers to monitor [{0}]".format(len(servers)), trace=True)
        for server in servers:
            if self.serverAlive(server.get('_id')):
                retVal = True
                continue
            else:
                self.ioc.getLogger().warning("Server [{0}] preparing to be culled from pool".format(server.get('_id')))
                self.ioc.getLogger().warning("Server [{0}] preparing to be deactivated".format(server.get('_id')))
                if not self.deactivateServer(server.get('_id')):
                    self.ioc.getLogger().error(
                        "Failed deactivating server [{0}]".format(server.get('_id'))
                    )
                    retVal = False
                    break
                self.ioc.getLogger().warning(
                    "Server [{0}] preparing to reallocate detect jobs".format(server.get('_id'))
                )
                if not self.rescheduleDetectJobs(server.get('_id')):
                    self.ioc.getLogger().error(
                        "Failed rescheduling detect jobs [{0}]".format(server.get('_id'))
                    )
                    retVal = False
                    break
                self.ioc.getLogger().warning(
                    "Server [{0}] preparing to reallocate schedule jobs".format(server.get('_id'))
                )
                if not self.rescheduleScheduleJobs(server.get('_id')):
                    self.ioc.getLogger().error(
                        "Failed rescheduling detect jobs [{0}]".format(server.get('_id'))
                    )
                    retVal = False
                    break
                self.ioc.getLogger().warning(
                    "Server [{0}] preparing to reallocate jobs".format(server.get('_id'))
                )
                if not self.rescheduleJobs(server.get('_id')):
                    self.ioc.getLogger().error(
                        "Failed rescheduling detect jobs [{0}]".format(server.get('_id'))
                    )
                    retVal = False
                    break
        return retVal

    def scanComplete(self):
        """Enters a completed source so that this local server is alive next run

        This method is so that the server's 'heart' beats after each run. It will insert a completed SourceData document
        and increments the job counter in the JobServer Document

        Returns:
            None: Writes a MongoDB Document

        """
        self.ioc.getCollection('SourceData').insert_one({
            'grease_data': {
                'sourcing': {
                    'server': ObjectId(self.ioc.getConfig().NodeIdentity)
                },
                'detection': {
                    'server': ObjectId(self.ioc.getConfig().NodeIdentity),
                    'start': datetime.datetime.utcnow(),
                    'end': datetime.datetime.utcnow(),
                    'detection': {}
                },
                'scheduling': {
                    'server': ObjectId(self.ioc.getConfig().NodeIdentity),
                    'start': datetime.datetime.utcnow(),
                    'end': datetime.datetime.utcnow()
                },
                'execution': {
                    'server': ObjectId(self.ioc.getConfig().NodeIdentity),
                    'assignmentTime': datetime.datetime.utcnow(),
                    'completeTime': datetime.datetime.utcnow(),
                    'returnData': {},
                    'executionSuccess': True,
                    'commandSuccess': True,
                    'failures': 0
                }
            },
            'source': 'grease_internal_node_monitoring',
            'configuration': None,
            'data': {},
            'createTime': datetime.datetime.utcnow(),
            'expiry': Deduplication.generate_max_expiry_time(1)
        })
        server = self.ioc.getCollection('JobServer').find_one({'_id': ObjectId(self.ioc.getConfig().NodeIdentity)})
        if not server:
            self.ioc.getLogger().critical(
                "Failed to find server [{0}] after monitoring occurred!".format(self.ioc.getConfig().NodeIdentity)
            )
        self.ioc.getCollection('JobServer').update_one({
            '_id': ObjectId(self.ioc.getConfig().NodeIdentity)},
            {'$set': {'jobs': dict(server).get('jobs', 0) + 1}}
        )

    def getServers(self):
        """Returns the servers to be monitored this cycle

        Returns:
            list[dict]: List of servers

        """
        final = []
        servers = self.ioc.getCollection('JobServer').find({'active': True})
        for server in servers:
            final.append(dict(server))
        return final

    def serverAlive(self, serverId):
        """Checks to see if server is alive

        This method checks if the serverID exists in the collection and determines if it's execution number has
        changed recently. If it is a newly configured node it will be added to the monitoring collection

        Args:
            serverId (str): ObjectId of server

        Returns:
            bool: If server is alive

        """
        # Server Health Collection
        coll = self.ioc.getCollection('ServerHealth')
        Server = coll.find_one({'server': ObjectId(serverId)})
        if Server:
            # We have a server already in the system
            serverStats = self.ioc.getCollection('JobServer').find_one({'_id': ObjectId(serverId)})
            if serverStats:
                # compare previous results to see if there has been change
                if dict(Server).get('jobs', 0) < dict(serverStats).get('jobs', 0):
                    # Job Server Numbers have changed
                    coll.update_one(
                        {'_id': Server['_id']},
                        {
                            '$set': {
                                'jobs': dict(serverStats).get('jobs', 0),
                                'checkTime': datetime.datetime.utcnow()
                            }
                        }
                    )
                    self.ioc.getLogger().trace("JobServer [{0}] is alive".format(serverId), trace=True)
                    return True
                else:
                    if dict(Server).get('checkTime', datetime.datetime.utcnow()) < \
                            datetime.datetime.utcnow() - datetime.timedelta(minutes=10):
                        # server has aged out
                        self.ioc.getLogger().trace(
                            "JobServer [{0}] is not alive; Timestamp has not changed in ten minutes".format(serverId),
                            trace=True
                        )
                        return False
                    else:
                        # server is in a degraded state
                        self.ioc.getLogger().warning("JobServer [{0}] is degraded!".format(serverId), trace=True)
                        return True
            else:
                # Failed to find server in JobServer collection
                self.ioc.getLogger().error("JobServer not found during node monitoring! [{0}]".format(serverId))
                return False
        else:
            # we have a new server
            serverStats = self.ioc.getCollection('JobServer').find_one({'_id': ObjectId(serverId)})
            if serverStats:
                coll.insert_one(
                    {
                        'server': ObjectId(serverId),
                        'jobs': dict(serverStats).get('jobs', 0),
                        'checkTime': datetime.datetime.utcnow()
                    }
                )
                self.ioc.getLogger().info("New JobServer persisted in monitoring [{0}]".format(serverId))
                return True
            else:
                # Failed to find server in JobServer collection
                self.ioc.getLogger().error("New JobServer not found during node monitoring! [{0}]".format(serverId))
                return False

    def deactivateServer(self, serverId):
        """deactivates server from pool

        Args:
            serverId (str): ObjectId to deactivate

        Returns:
            bool: If deactivation is successful

        """
        if self.ioc.getCollection('JobServer').update_one(
                {'_id': ObjectId(serverId)},
                {
                    '$set': {
                        'active': False
                    }
                }
        ).modified_count < 1:
            self.ioc.getLogger().warning("Server [{0}] failed to be deactivated".format(serverId))
            return False
        else:
            self.ioc.getLogger().warning("Server [{0}] deactivated".format(serverId))
            return True

    def rescheduleDetectJobs(self, serverId):
        """Reschedules any detection jobs

        Args:
            serverId (str): Server ObjectId

        Returns:
            bool: rescheduling success

        """
        retval = True
        server = self.ioc.getCollection('JobServer').find_one({'_id': ObjectId(serverId)})
        if not server:
            self.ioc.getLogger().error(
                "Failed to load server details while trying to reschedule detection [{0}]".format(serverId)
            )
            return False
        for job in self.ioc.getCollection('SourceData').find(
            {
                'grease_data.detection.server': ObjectId(serverId),
                'grease_data.detection.start': None,
                'grease_data.detection.end': None
            }
        ):
            job = dict(job)
            if not self.centralScheduler.scheduleDetection(job.get('source'), job.get('configuration'), [job]):
                retval = False
                break
            else:
                self.ioc.getCollection('JobServer').update_one(
                    {'_id': ObjectId(serverId)},
                    {
                        '$set': {
                            'jobs': dict(server).get('jobs', 0) - 1
                        }
                    }
                )
        return retval

    def rescheduleScheduleJobs(self, serverId):
        """Reschedules any detection jobs

        Args:
            serverId (str): Server ObjectId

        Returns:
            bool: rescheduling success

        """
        retval = True
        server = self.ioc.getCollection('JobServer').find_one({'_id': ObjectId(serverId)})
        if not server:
            self.ioc.getLogger().error(
                "Failed to load server details while trying to reschedule schedules [{0}]".format(serverId)
            )
            return False
        for job in self.ioc.getCollection('SourceData').find(
            {
                'grease_data.scheduling.server': ObjectId(serverId),
                'grease_data.scheduling.start': None,
                'grease_data.scheduling.end': None
            }
        ):
            job = dict(job)
            if not self.centralScheduler.scheduleScheduling(job.get('_id')):
                retval = False
                break
            else:
                self.ioc.getCollection('JobServer').update_one(
                    {'_id': ObjectId(serverId)},
                    {
                        '$set': {
                            'jobs': dict(server).get('jobs', 0) - 1
                        }
                    }
                )
        return retval

    def rescheduleJobs(self, serverId):
        """Reschedules any detection jobs

        Args:
            serverId (str): Server ObjectId

        Returns:
            bool: rescheduling success

        """
        retval = True
        server = self.ioc.getCollection('JobServer').find_one({'_id': ObjectId(serverId)})
        if not server:
            self.ioc.getLogger().error(
                "Failed to load server details while trying to reschedule schedules [{0}]".format(serverId)
            )
            return False
        for job in self.ioc.getCollection('SourceData').find(
            {
                'grease_data.execution.server': ObjectId(serverId),
                'grease_data.execution.commandSuccess': False,
                'grease_data.execution.executionSuccess': False,
                'grease_data.execution.failures': {'$lt': 6}
            }
        ):
            job = dict(job)
            if not self.scheduler.schedule(job):
                retval = False
                break
            else:
                self.ioc.getCollection('JobServer').update_one(
                    {'_id': ObjectId(serverId)},
                    {
                        '$set': {
                            'jobs': dict(server).get('jobs', 0) - 1
                        }
                    }
                )
        return retval
