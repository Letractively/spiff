from Exception import WorkflowException
from Activity  import Activity

class StructuredSynchronizingMerge(Activity):
    """
    This class represents an activity for synchronizing branches that were
    previously split using a conditional activity, such as MultiChoice.
    It has two or more inputs and one or more outputs.
    """

    def __init__(self, parent, name, split_activity):
        """
        Constructor.
        
        parent -- a reference to the parent (Activity)
        name -- a name for the pattern (string)
        split_activity -- the activity that was previously used to split the
                          branch
        """
        assert split_activity is not None
        Activity.__init__(self, parent, name)
        self.split_activity = split_activity


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
        # already received.
        assert job.get_context_data(self, 'may_fire', False) == False

        # Retrieve a list of all activated branches from the associated
        # activity that did the conditional parallel split.
        branches = self.split_activity.get_activated_branches(job)

        # Look up which branches have already completed.
        default   = dict([(repr(br), False) for br in branches])
        completed = job.get_context_data(self, 'completed', default)

        # Make sure that the current notification is not a duplicate.
        assert completed[repr(branch)] == False
        completed[repr(branch)] = True

        # If all branches are now completed, reset the state.
        if completed.values().count(False) == 0:
            job.del_context_data(self, 'completed')
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
        assert job    is not None
        assert branch is not None
        self.test()

        # Make sure that all inputs have completed.
        if job.get_context_data(self, 'may_fire', False) == False:
            return False

        job.set_context_data(self, may_fire = False)
        return Activity.execute(self, job, branch)
