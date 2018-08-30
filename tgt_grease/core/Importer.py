import importlib
from tgt_grease.core import Logging


class ImportTool(object):
    """Import Tooling for getting instances of classes automatically

    Attributes:
        _log (Logging): Logger for the class

    """

    _log = None

    def __init__(self, logger):
        if not isinstance(logger, Logging):
            raise Exception("Invalid Constructor, logger element not of type Logging class")
        else:
            self._log = logger

    def load(self, className):
        """Dynamic loading of classes for the system

        Args:
            className (str): Class name to search for

        Returns:
            object: If an object is found it is returned
            None: If an object is not found and error occurs None is returned

        """
        if not className: # Catches None, empty string, etc.
            self._log.error(
                        "TYPEERROR: [{0}] is not a valid classname (it is a {1}, not a string). Load failed.".format(className, type(className)),
                        verbose=True
                    )
            return None

        self._log.trace("Attempting to load class [{0}]".format(className), trace=True)
        for path in self._log.getConfig().get('Import', 'searchPath'):
            self._log.trace("Searching path [{0}]".format(path), trace=True)
            try:
                SearchModule = importlib.import_module(str(path))
            except ImportError:
                self._log.error("Failed to import module [{0}]".format(path), verbose=True)
                continue
            if not className.startswith("__") and self._dir_contains(SearchModule, className):
                try:
                    req = self._get_attr(SearchModule, str(className))
                    instance = req()
                    return instance
                except AttributeError:
                    self._log.error(
                        "ATTRERROR: Failed to create instance of class [{0}] from module [{1}]".format(className, path),
                        verbose=True
                    )
                except TypeError:
                    self._log.error(
                        "TYPEERROR: Failed to create instance of class [{0}] from module [{1}]".format(className, path),
                        verbose=True
                    )
                except Exception as e:
                    self._log.error(
                        "{0}: Failed to create instance of class [{1}] from module [{2}]".format(str(type(e)).upper(), className, path),
                        verbose=True
                    )
        return None

    def _get_attr(self, object, name, default=None):
        """Wrapper function for the built-in getattr function. Wrapper is required to mock the built-in function.

        Args:
            object (Any object): Object you are searching for a named attribute for
            name (str): Name of the attribute you want to get from object
            default (Any object): Return value if attribute name is not found in object. Raises exception if no default is provided.

        Returns:
            object: If an attribute is found it is returned. If it is not found, default is returned. 

        """
        return getattr(object, name, default)

    def _dir_contains(self, module, name):
        """Wrapper function for built in dir function. Needed for mocking. 

        Args:
            module (module): Module you are searching, imported with importlib.import_module
            name (str): Attribute (class) name you are searching the module for

        Returns:
            Bool: Returns true if module contains name, else false.
        """
        return name in dir(module)
