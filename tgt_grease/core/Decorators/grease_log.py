import inspect
from functools import wraps
# Ran into circular imports, so using long classpaths
import tgt_grease


def grease_log(decorator=None, *, level="info", notify=False, verbose=False):
    def _decorate(wrapped):

        @wraps(wrapped)
        def log(*args, **kwargs):
            # Get the first instance of a command or source from the stack
            stack = inspect.stack()

            calling_class = "Unknown"
            for stack_item in stack:
                self_context = stack_item[0].f_locals.get("self")
                if isinstance(self_context, tgt_grease.core.Types.Command) or \
                        isinstance(self_context, tgt_grease.enterprise.Model.BaseSourceClass):
                    calling_class = self_context.__class__.__name__
                    break

            ioc = tgt_grease.core.GreaseContainer()

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

            logger("Starting execution of {0} from Command or Source {1}.".format(wrapped.__name__, calling_class),
                   verbose=verbose, notify=notify)
            wrapped(*args, **kwargs)
            logger("Finished execution of {0} from Command or Source {1}.".format(wrapped.__name__, calling_class),
                   verbose=verbose, notify=notify)
        return log

    # This allows it to be called as a bare decorator (i.e. @grease_log), or with arguments.
    if decorator:
        return _decorate(decorator)

    return _decorate

