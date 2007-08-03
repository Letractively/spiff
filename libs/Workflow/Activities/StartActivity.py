from Exception import WorkflowException
from Activity  import Activity

class StartActivity(Activity):
    """
    This class implements the activity the is placed at the beginning
    of each workflow. The activity has no inputs and at least one output.
    If more than one output is connected, the activity does an implicit
    parallel split.
    """

    def __init__(self, parent):
        """
        Constructor.
        
        parent -- a reference to the parent (Activity)
        """
        Activity.__init__(self, parent, 'Start')


    def connect_notify(self, activity):
        """
        Called by the previous activity to let us know that it exists.
        """
        raise WorkflowException(self, 'StartActivity can not have any inputs.')


    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        if len(self.inputs) != 0:
            raise WorkflowException(self, 'StartActivity with an input.')
        elif len(self.outputs) < 1:
            raise WorkflowException(self, 'No output activity connected.')
