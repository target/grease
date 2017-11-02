from tgt_grease.core.Types import Command


class Help(Command):
    def __init__(self):
        super(Help, self).__init__()

    def execute(self, context):
        print("Welcome to GREASE Help")
        return True
