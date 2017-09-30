from abc import ABCMeta, abstractmethod
import tgt_grease_daemon.GreaseRouter
import os
import sys
import atexit
import time
from signal import SIGTERM
from collections import deque


class GreaseDaemonCommon(object):
    __metaclass__ = ABCMeta

    def __init__(self, router):
        # type: (tgt_grease_daemon.GreaseRouter.Router) -> None
        self._type = 'null'
        self._router = router
        self.args = deque(sys.argv)

    def get_type(self):
        # type: () -> str
        return str(self._type)

    def set_router(self, router):
        self._router = router

    def run(self):
        self._router.job_processor()

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def restart(self):
        pass


class WindowsService(GreaseDaemonCommon):

    def __init__(self, args, router=None):
        # raise SystemError("Windows Daemons are not supported Yet")
        if not isinstance(router, tgt_grease_daemon.GreaseRouter.Router):
            raise AttributeError("Router Instance Not Detected: " + str(type(router)))
        GreaseDaemonCommon.__init__(self, router)
        self.set_router(router)

    def restart(self):
        self.stop()
        self.start()

    def stop(self):
        self._router._grease.message().info("Service Stop")
        sys.exit(0)

    def start(self):
        self._router.job_processor()


class UnixDaemon(GreaseDaemonCommon):

    def __init__(self, router):
        super(UnixDaemon, self).__init__(router)
        self._pidfile = '/tmp/grease/grease.pid'
        self._pid = os.getpid()

    def daemonize(self):
        """Standard Double Fork"""
        # First Fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit Parent Now
                sys.exit(0)
        except OSError as e:
            self._router._grease.message().exception("Fork Failure [1]: {0} ({1})".format(e.errno, e.strerror))
            self._router.bad_exit("Fork Failure: {0} ({1})".format(e.errno, e.strerror), 2)
        # Decouple from the parent process env data
        os.chdir("/")
        os.setsid()
        os.umask(0)
        # Second Fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit Parent Now
                sys.exit(0)
        except OSError as e:
            self._router._grease.message().exception("Fork Failure [2]: {0} ({1})".format(e.errno, e.strerror))
            self._router.bad_exit("Fork Failure: {0} ({1})".format(e.errno, e.strerror), 2)
        # Finally lets write our pid file
        # Register Our Daemon
        atexit.register(self.del_pid)
        pid = str(os.getpid())
        file(self._pidfile, 'w+').write(str(pid))
        self._pid = pid

    def del_pid(self):
        os.remove(str(self._pidfile))

    def restart(self):
        self.stop()
        self.start()

    def stop(self):
        # Attempt to get lock on PID
        try:
            pidfile = file(self._pidfile, 'r')
            pid = int(pidfile.read().strip())
            pidfile.close()
        except IOError:
            pid = None
        # If there was no File / Pid Found
        if not pid:
            self._router._grease.message().error("Daemon Not Running Cannot Stop")
            self._router.bad_exit("Daemon Is Not Running Currently, Failed To Stop", 3)
        # try to kill the running PID
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self._pidfile):
                    os.remove(self._pidfile)
            else:
                self._router._grease.message().exception(err)
                self._router.bad_exit(err,4)

    def start(self):
        # First check if daemon is already running
        try:
            pidfile = file(self._pidfile, 'r')
            pid = int(pidfile.read().strip())
            pidfile.close()
        except IOError:
            pid = None
        # if already in Daemon then ignore else start
        if pid:
            self._router._grease.message().info("Daemon already running")
            print("Daemon Already In Service")
            sys.exit(0)
        else:
            self.daemonize()
            self.run()

