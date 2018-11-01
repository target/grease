import inspect
from tgt_grease.core.InversionOfControl import GreaseContainer
from tgt_grease.enterprise.Model import BaseSourceClass
from tgt_grease.core.Types import Command


def grease_log(wrapped):
    def log(*args, **kwargs):
        stack = inspect.stack()
        for stack_item in stack:
            self_context = stack_item[0].f_locals.get("self")
            if isinstance(self_context, Command) or isinstance(self_context, BaseSourceClass):
                calling_class = self_context.__class__.__name__
                break
            else:
                calling_class = "Unknown"
                break

        GreaseContainer().getLogger().info(f"Starting execution of {wrapped.__name__} from class {calling_class}.")
        wrapped(*args, **kwargs)
        GreaseContainer().getLogger().info(f"Finished execution of {wrapped.__name__} from class {calling_class}.")

    return log

