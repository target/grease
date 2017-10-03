from .Scanner import ScanOnConfig
from .Detector import Detector
from .Scheduler import Scheduler
from tgt_grease_daemon.BaseCommand import GreaseDaemonCommand


class CaptainKirk(GreaseDaemonCommand):
    def __init__(self):
        super(CaptainKirk, self).__init__()

    def execute(self, context='{}'):
        instance = ScanOnConfig()
        self._ioc.message().debug("Scanning Sources")
        instance.execute()
        self._ioc.message().debug("Parsing Sources")
        instance = Detector()
        instance.execute()
        self._ioc.message().debug("Scheduling Jobs")
        instance = Scheduler()
        instance.execute()
        return True
