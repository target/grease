from tgt_grease.core.Types import Command
from tgt_grease.enterprise.Model import Scheduler


class Scheduling(Command):
    """The schedule command

    This class is the job scheduling for GREASE. It utilizes the job and exe_env (if provided) keys of your configurations
    to schedule jobs for execution

    """

    __author__ = "James E. Bell Jr."
    __version__ = "2.0.0"
    purpose = "Schedule detected Jobs for Execution"
    help = """
    This command schedules jobs for execution
    
    Args:
        --loop:<int>
            How many scheduling cycles to do
        --foreground
            Print log messages to the foreground
    """

    def execute(self, context):
        """Execute method of the scheduling

        Args:
            context (dict): Command Context

        Note:
            This method normally will *never* return. As it is a prototype. So it should continue into infinity

        Returns:
             bool: True always unless failures occur

        """
        if context.get('foreground'):
            # set foreground if in context
            self.ioc.getLogger().foreground = True
        Sch = Scheduler(self.ioc)
        if 'loop' in context:
            # scan only a certain amount of times
            scan_count = 0
            while scan_count < int(context.get('loop')):
                if not Sch.scheduleExecution():
                    self.ioc.getLogger().warning("Scheduling Process Failed", notify=False)
                scan_count += 1
        else:
            try:
                while True:
                    if not Sch.scheduleExecution():
                        self.ioc.getLogger().warning("Scheduling Process Failed", notify=False)
                    continue
            except KeyboardInterrupt:
                # graceful close for scanning
                self.ioc.getLogger().trace("Keyboard interrupt in detect detected", trace=True)
                return True
        # ensure we clean up after ourselves
        if context.get('foreground'):
            self.ioc.getLogger().foreground = False
        return True
