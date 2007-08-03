from Exception import WorkflowException
from Activity  import Activity

class Synchronization(Activity):
    """
    This class represents a synchronization activity in the workflow.
    It has two or more inputs and one or more outputs.
    """

    def __init__(self, parent, name):
        """
        Constructor.
        
        parent -- a reference to the parent (Activity)
        name -- a name for the pattern (string)
        """
        Activity.__init__(self, parent, name)


    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        Activity.test(self)
        if len(self.inputs) < 2:
            error = 'Less than two input activities connected.'
            raise WorkflowException(self, error)


    def completed_notify(self, job, branch, activity):
        # It is an error if this method is called after all inputs were
        # already received,
        assert job.get_context_data(self, 'may_fire', False) == False

        # Look up which branches have already completed.
        default   = dict([(repr(input), False) for input in self.inputs])
        completed = job.get_context_data(self, 'completed', default)

        # Make sure that the current notification is not a duplicate.
        assert completed[repr(activity)] == False
        completed[repr(activity)] = True

        # If all branches are now completed, reset the state.
        if completed.values().count(False) == 0:
            job.set_context_data(self, completed = default)
            job.set_context_data(self, may_fire  = True)
            return

        # Merge all except for the last branch.
        job.set_context_data(self, completed = completed)
        job.branch_completed_notify(branch)


    def execute(self, job, branch):
        """
        Runs the activity. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        assert job is not None
        assert branch is not None
        self.test()

        # Make sure that all inputs have completed.
        if job.get_context_data(self, 'may_fire', False) == False:
            return False

        return Activity.execute(self, job, branch)
