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
from BranchNode import *
from Exception  import WorkflowException
from Activity   import Activity

class Synchronization(Activity):
    """
    This class represents an activity for synchronizing branch_nodes that were
    previously split using a conditional activity, such as MultiChoice.
    It has two or more inputs and one or more outputs.
    """

    def __init__(self, parent, name, split_activity = None):
        """
        Constructor.
        
        parent -- a reference to the parent (Activity)
        name -- a name for the pattern (string)
        split_activity -- the activity that was previously used to split the
                          branch_node
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


    def _completed_notify_structured(self, job, branch_node, activity):
        # The context is the path up to the point where the split happened.
        context = branch_node.get_path(None, self.split_activity)

        # It is an error if this method is called after all inputs were
        # already received.
        assert job.get_context_data(context, 'may_fire', False) == False

        # Retrieve a list of all activated branch_nodes from the associated
        # activity that did the conditional parallel split.
        branch_nodes = self.split_activity.get_activated_branch_nodes(job, branch_node)

        # Look up which branch_nodes have already completed.
        default   = dict([(repr(br.id), False) for br in branch_nodes])
        completed = job.get_context_data(context, 'completed', default)

        # Make sure that the current notification is not a duplicate.
        branch_start_node = branch_node.get_branch_start()
        assert completed[repr(branch_start_node.id)] == False
        completed[repr(branch_start_node.id)] = True

        # If all branch_nodes are now completed, reset the state.
        if completed.values().count(False) == 0:
            job.del_context_data(context, 'completed')
            job.set_context_data(context, may_fire  = True)
            return

        # Merge all except for the last branch_node.
        job.set_context_data(context, completed = completed)
        branch_node.drop_children()
        branch_node.activity_status_changed_notify(activity, COMPLETED)


    def _completed_notify_unstructured(self, job, branch_node, activity):
        # The context is the path up to this activity.
        context = self.id

        # It is an error if this method is called after all inputs were
        # already received,
        assert job.get_context_data(context, 'may_fire', False) == False

        # Look up which branch_nodes have already completed.
        default   = dict([(repr(input.id), False) for input in self.inputs])
        completed = job.get_context_data(context, 'completed', default)

        # Make sure that the current notification is not a duplicate.
        assert completed[repr(activity.id)] == False
        completed[repr(activity.id)] = True

        # If all branch_nodes are now completed, reset the state.
        if completed.values().count(False) == 0:
            job.set_context_data(context, completed = default)
            job.set_context_data(context, may_fire  = True)
            return

        # Merge all except for the last branch_node.
        job.set_context_data(context, completed = completed)
        branch_node.drop_children()
        branch_node.activity_status_changed_notify(activity, COMPLETED)


    def completed_notify(self, job, branch_node, activity):
        if self.split_activity is None:
            return self._completed_notify_unstructured(job, branch_node, activity)
        return self._completed_notify_structured(job, branch_node, activity)


    def execute(self, job, branch_node):
        """
        Runs the activity. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        assert job    is not None
        assert branch_node is not None
        self.test()

        # The context is the path up to the point where the split happened.
        if self.split_activity is None:
            context = self.id
        else:
            context = branch_node.get_path(None, self.split_activity)

        # Make sure that all inputs have completed.
        if job.get_context_data(context, 'may_fire', False) == False:
            return False

        job.set_context_data(context, may_fire = False)
        return Activity.execute(self, job, branch_node)
