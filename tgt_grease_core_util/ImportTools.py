import importlib
from tgt_grease_core_util.Logging import Logger


class Importer(object):
    def __init__(self, logger):
        # type: (Logger) -> None
        self.purpose = "to load modules"
        self._log = logger

    def load(self, module_name, module_class, fully_qualified=False):
        import inspect
        # type: (str, str, bool) -> object
        try:
            if bool(fully_qualified):
                loaded_module = importlib.import_module(str(module_name))
            else:
                loaded_module = importlib.import_module('tgt_grease_' + str(module_name))
            try:
                req = getattr(loaded_module, module_class)
                instance = req()
                return instance
            except AttributeError as a:
                self._log.error("Failed to create instance of class::[" + str(a) + "]")
                return None
        except ImportError as i:
            self._log.error("Failed to Import Module::[" + str(i) + "] [" +
                            str(inspect.getouterframes(inspect.currentframe())[1])
                        + "]")
            return None
