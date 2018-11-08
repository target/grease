import inspect
from functools import wraps


def grease_log(_decorator=None, before_message="", after_message="", level="info", notify=False, verbose=False):
    """Decorator that will call GREASE's logger before and after the wrapped function

        Parameters:
            _decorator (function): Internal - do not use.
            before_message (str): The message to log before calling the wrapped function. Defaults to
                "Starting execution of {0} from Command or Source {1}." where {0} is the function name and {1} is the
                calling command or source's name
            after_message (str): The message to log after calling the wrapped function. Defaults to
                "Finished execution of {0} from Command or Source {1}." where {0} is the function name and {1} is the
                calling Command or Source's name
            level (str): A function name from the Logging class (trace, debug, info, warning, error, critical)
            notify (bool): True to notify the appropriate channels as configured in grease.conf.json
            verbose (bool): True to log in verbose mode

        """

    def _decorate(wrapped):

        @wraps(wrapped)
        def log(*args, **kwargs):
            # Importing here to prevent circular imports
            from tgt_grease.core.Types import Command
            from tgt_grease.enterprise.Model import BaseSourceClass
            from tgt_grease.core import GreaseContainer

            ioc = GreaseContainer()

            # Get the correct logging function
            if level.lower() == "critical":
                logger = ioc.getLogger().critical
            elif level.lower() == "error":
                logger = ioc.getLogger().error
            elif level.lower() == "warning":
                logger = ioc.getLogger().warning
            elif level.lower() == "debug":
                logger = ioc.getLogger().debug
            elif level.lower() == "trace":
                logger = ioc.getLogger().trace
            else:
                logger = ioc.getLogger().info

            # Get the first instance of a command or source from the stack
            stack = inspect.stack()

            calling_class = "Unknown"
            for stack_item in stack:
                self_context = stack_item[0].f_locals.get("self")
                if isinstance(self_context, Command) or \
                        isinstance(self_context, BaseSourceClass):
                    calling_class = self_context.__class__.__name__
                    break

            before_msg = before_message if before_message else \
                "Starting execution of {0} from Command or Source {1}.".format(wrapped.__name__, calling_class)

            after_msg = after_message if after_message else \
                "Finished execution of {0} from Command or Source {1}.".format(wrapped.__name__, calling_class)

            logger(before_msg, verbose=verbose, notify=notify)
            wrapped(*args, **kwargs)
            logger(after_msg, verbose=verbose, notify=notify)
        return log

    # This allows it to be called as a bare decorator (i.e. @grease_log), or with arguments.
    if _decorator:
        return _decorate(_decorator)

    return _decorate
