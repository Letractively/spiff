# Copyright (C) 2007 Samuel Abels
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
from Exception import WorkflowException
from Activity  import Activity

class Synchronization(Activity):
    """
    This class represents an activity for synchronizing branches that were
    previously split using a conditional activity, such as MultiChoice.
    It has two or more inputs and one or more outputs.
    """

    def __init__(self, parent, name, split_activity = None):
        """
        Constructor.
        
        parent -- a reference to the parent (Activity)
        name -- a name for the pattern (string)
        split_activity -- the activity that was previously used to split the
                          branch
        """
        #assert split_activity is not None
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


    def _completed_notify_structured(self, job, branch, activity):
        # The context is the path up to the point where the split happened.
        context = branch.get_path(None, self.split_activity)

        # It is an error if this method is called after all inputs were
        # already received.
        assert job.get_context_data(context, 'may_fire', False) == False

        # Retrieve a list of all activated branches from the associated
        # activity that did the conditional parallel split.
        branches = self.split_activity.get_activated_branches(job, branch)

        # Look up which branches have already completed.
        default   = dict([(repr(br), False) for br in branches])
        completed = job.get_context_data(context, 'completed', default)

        # Make sure that the current notification is not a duplicate.
        assert completed[repr(branch)] == False
        completed[repr(branch)] = True

        # If all branches are now completed, reset the state.
        if completed.values().count(False) == 0:
            job.del_context_data(context, 'completed')
            job.set_context_data(context, may_fire  = True)
            return

        # Merge all except for the last branch.
        job.set_context_data(context, completed = completed)
        job.branch_completed_notify(branch)


    def _completed_notify_unstructured(self, job, branch, activity):
        # The context is the path up to this activity.
        context = self.id

        # It is an error if this method is called after all inputs were
        # already received,
        assert job.get_context_data(context, 'may_fire', False) == False

        # Look up which branches have already completed.
        default   = dict([(repr(input), False) for input in self.inputs])
        completed = job.get_context_data(context, 'completed', default)

        # Make sure that the current notification is not a duplicate.
        assert completed[repr(activity)] == False
        completed[repr(activity)] = True

        # If all branches are now completed, reset the state.
        if completed.values().count(False) == 0:
            job.set_context_data(context, completed = default)
            job.set_context_data(context, may_fire  = True)
            return

        # Merge all except for the last branch.
        job.set_context_data(context, completed = completed)
        job.branch_completed_notify(branch)


    def completed_notify(self, job, branch, activity):
        if self.split_activity is None:
            return self._completed_notify_unstructured(job, branch, activity)
        return self._completed_notify_structured(job, branch, activity)


    def execute(self, job, branch):
        """
        Runs the activity. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        assert job    is not None
        assert branch is not None
        self.test()

        # The context is the path up to the point where the split happened.
        if self.split_activity is None:
            context = self.id
        else:
            context = branch.get_path(None, self.split_activity)

        # Make sure that all inputs have completed.
        if job.get_context_data(context, 'may_fire', False) == False:
            return False

        job.set_context_data(context, may_fire = False)
        return Activity.execute(self, job, branch)
