from tgt_grease.core import GreaseContainer
from .Configuration import PrototypeConfig
from tgt_grease.core import ImportTool
from .CentralScheduling import Scheduling
import multiprocessing as mp

class KafkaSource(object):

    def __init__(self, ioc=None):
        if ioc and isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()
        self.conf = PrototypeConfig(self.ioc)
        self.impTool = ImportTool(self.ioc.getLogger())
        self.scheduler = Scheduling(self.ioc)
        self.configs = []

    @staticmethod
    def consume(conf):
        return True

    def run(self, config=None):
        if config:
            self.configs = [config]
        else:
            self.configs = self.get_configs()


        procs = []
        for conf in self.configs:
            proc = mp.Process(target=KafkaSource.consume, args=(conf,))
            proc.daemon = False
            proc.start()
            procs.append(proc)

    def get_configs(self):
        return []
