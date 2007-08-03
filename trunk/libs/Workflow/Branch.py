from Trackable import Trackable

class Branch(Trackable):
    """
    This class implements a branch (= a taken path) within the workflow.
    """

    def __init__(self, id, job, first_activity):
        """
        Constructor.
        """
        assert id             is not None
        assert job            is not None
        assert first_activity is not None
        Trackable.__init__(self)
        self.id         = id
        self.job        = job
        self.path       = [first_activity] # The path of taken/next activities.
        self.current    = 0


    def copy(self, id):
        """
        Returns a copy of this branch.

        id -- the id of the new copy
        """
        branch      = Branch(id, self.job, self.path[0])
        branch.path = self.path[:]
        return branch


    def clear_queue(self):
        self.path = self.path[:self.current]


    def queue_next_activity(self, activity):
        """
        Called by an activity to activate its successor in the workflow.
        """
        assert activity is not None
        self.path.append(activity)


    def activity_completed_notify(self, activity):
        """
        Called by an activity when it is completed.
        """
        assert activity == self.path[self.current]
        self.current += 1


    def execute_next(self):
        """
        Executes the next activity in the branch if it is ready to run.
        Returns True if the activity was executed, False otherwise.
        """
        assert self.id >= 0
        next_activity = self.path[self.current]
        if len(next_activity.outputs) == 0:
            self.job.branch_completed_notify(self)
            return False
        return next_activity.execute(self.job, self)
