from Exception import WorkflowException
from Activity  import Activity

class StubActivity(Activity):
    """
    This class implements the activity that is placed at the end of each
    workflow. It has one or more inputs and no outputs.
    If more than one input is connected, the activity does an implicit
    simple merge.
    """

    def __init__(self, parent, name):
        """
        Constructor.
        
        parent -- a reference to the parent (Activity)
        name -- a name for the pattern (string)
        """
        Activity.__init__(self, parent, name)


    def connect(self, activity):
        """
        Connect the *following* activity to this one. In other words, the
        given activity is added as an output activity.
        """
        raise WorkflowException(self, 'StubActivity can not have any outputs.')


    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        if len(self.inputs) < 1:
            raise WorkflowException(self, 'No input activity connected.')
        elif len(self.outputs) != 0:
            raise WorkflowException(self, 'StubActivity with an output.')


    def execute(self, job, branch):
        """
        Runs the activity.
        """
        raise WorkflowException(self, 'StubActivity can not be executed.')
