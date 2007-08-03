from Activities import StartActivity
from Activities import StubActivity

class Workflow(object):
    """
    This class represents an entire workflow.
    """

    def __init__(self, name = ''):
        """
        Constructor.
        """
        self.name       = name
        self.activities = []
        self.start      = StartActivity(self)
        self.end        = StubActivity(self, 'End')


    def add(self, activity):
        self.activities.append(activity)
