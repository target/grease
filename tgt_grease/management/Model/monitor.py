from tgt_grease.core import GreaseContainer
from bson.objectid import ObjectId
import datetime


class NodeMonitoring(object):
    """Monitors cluster nodes for unhealthy state

    Attributes:
        ioc (GreaseContainer): IoC Access

    """

    def __init__(self, ioc=None):
        if isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()

    def monitor(self):
        """Monitoring process

        Returns:
            bool: If successful monitoring run occurred

        """
        servers = self.getServers()
        self.ioc.getLogger().debug("Total servers to monitor [{0}]".format(len(servers)), trace=True)
        for server in servers:
            if self.serverAlive(server.get('_id')):
                continue
            else:
                # TODO: Culling
                self.ioc.getLogger().error("Server [{0}] preparing to be culled from pool".format(server.get('_id')))
        return True

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
