from Exception import WorkflowException
from Trackable import Trackable

class Activity(Trackable):
    """
    This class implements a activity with one or more inputs and
    one or more outputs.
    If more than one input is connected, the activity does an implicit
    multi merge.
    If more than one output is connected, the activity does an implicit
    parallel split.
    """

    def __init__(self, parent, name):
        """
        Constructor.

        parent -- a reference to the parent (Activity)
        name -- a name for the pattern (string)
        """
        Trackable.__init__(self)
        assert parent is not None
        assert name   is not None
        self._parent   = parent
        self.name      = name
        self.inputs    = []
        self.outputs   = []
        self.user_func = None
        self.manual    = False
        self._parent.add(self)


    def connect(self, activity):
        """
        Connect the *following* activity to this one. In other words, the
        given activity is added as an output activity.
        """
        self.outputs.append(activity)
        activity.connect_notify(self)


    def connect_notify(self, activity):
        """
        Called by the previous activity to let us know that it exists.

        activity -- the activity in which this method is executed
        """
        self.inputs.append(activity)


    def completed_notify(self, job, branch, activity):
        """
        Called by the previous activity to let us know that it has finished.

        job -- the job in which this method is executed
        branch -- the branch in which this method is executed
        activity -- the activity in which this method is executed
        """
        pass


    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        if len(self.inputs) < 1:
            raise WorkflowException(self, 'No input activity connected.')
        elif len(self.outputs) < 1:
            raise WorkflowException(self, 'No output activity connected.')


    def execute(self, job, branch):
        """
        Runs the activity. Should not be called directly.
        Returns True if completed, False otherwise.

        job -- the job in which this method is executed
        branch -- the branch in which this method is executed
        """
        assert job is not None
        assert branch is not None
        self.test()

        # Run user code, if any.
        if self.user_func is not None:
            self.user_func(job, branch, self)

        # Notify the next activity.
        self.outputs[0].completed_notify(job, branch, self)
        branch.queue_next_activity(self.outputs[0])

        # If we have more than one output, implicitly split.
        for output in self.outputs[1:]:
            new_branch = job.split_branch(branch)
            new_branch.queue_next_activity(output)
            output.completed_notify(job, new_branch, self)

        branch.activity_completed_notify(self)
        return True
