import inspect
from tgt_grease.core.InversionOfControl import GreaseContainer
from tgt_grease.enterprise.Model import BaseSourceClass
from tgt_grease.core.Types import Command


def grease_log(wrapped):
    def log(*args, **kwargs):
        # Get the first instance of a command or source from the stack
        stack = inspect.stack()
        
        calling_class = "Unknown"
        for stack_item in stack:
            self_context = stack_item[0].f_locals.get("self")
            if isinstance(self_context, Command) or isinstance(self_context, BaseSourceClass):
                calling_class = self_context.__class__.__name__
                break

        ioc = GreaseContainer()

        ioc.getLogger().info(f"Starting execution of {wrapped.__name__} from Command or Source {calling_class}.")
        wrapped(*args, **kwargs)
        ioc.getLogger().info(f"Finished execution of {wrapped.__name__} from Command or Source {calling_class}.")

    return log

