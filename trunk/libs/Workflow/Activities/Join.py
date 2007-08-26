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

class Join(Activity):
    """
    This class represents an activity for synchronizing branch_nodes that were
    previously split using a conditional activity, such as MultiChoice.
    It has two or more incoming branches and one or more outputs.
    """

    def __init__(self, parent, name, split_activity = None, **kwargs):
        """
        Constructor.
        
        parent -- a reference to the parent (Activity)
        name -- a name for the pattern (string)
        split_activity -- the activity that was previously used to split the
                          branch_node
        kwargs -- may contain the following keys:
                      threshold -- an integer that specifies how many incoming
                      branches need to complete before the activity triggers.
                      When the limit is reached, the activity fires but still
                      expects all other branches to complete.
                      cancel -- when set to True, remaining incoming branches
                      are cancelled as soon as the discriminator is activated.
        """
        #assert split_activity is not None
        Activity.__init__(self, parent, name)
        self.split_activity = split_activity
        self.threshold      = kwargs.get('threshold', None)
        self.cancel         = kwargs.get('cancel',    False)


    def _completed_notify_structured(self, job, branch_node):
        # The context is the path up to the point where the split happened.
        context = branch_node.find_path(None, self.split_activity)

        # If the threshold was already reached, there is nothing else to do.
        if job.get_context_data(context, 'may_fire', 'no') != 'no':
            return

        # Retrieve a list of all activated branch_nodes from the associated
        # activity that did the conditional parallel split.
        branch_nodes = self.split_activity.get_activated_branch_nodes(job, branch_node)

        # Look up which branch_nodes have already completed.
        default   = dict([(repr(br.id), False) for br in branch_nodes])
        completed = job.get_context_data(context, 'completed', {})
        default.update(completed)
        completed = default

        # Find the point at which the branch started.
        split_node = branch_node.find_ancestor(self.split_activity)
        start_node = branch_node.get_child_of(split_node)

        # Make sure that the current notification is not a duplicate.
        assert completed[repr(start_node.id)] == False
        completed[repr(start_node.id)] = True

        # If the threshold was reached, get ready to fire.
        n_completed = completed.values().count(True)
        if n_completed == len(completed) \
          or (self.threshold is not None and n_completed >= self.threshold):
            job.set_context_data(context, may_fire = 'yes')

            # If this is a cancelling join, cancel all incoming branches,
            # except for the one that just completed.
            if self.cancel:
                nodes = self.split_activity.get_activated_branch_nodes(job, branch_node)
                nodes.remove(start_node)
                for node in nodes:
                    node.cancel()

            return

        # Merge all except for the last branch_node.
        job.set_context_data(context, completed = completed)
        branch_node.drop_children()
        branch_node.set_status(COMPLETED)


    def _completed_notify_unstructured(self, job, branch_node):
        # If the threshold was already reached, there is nothing else to do.
        context = self.id
        if job.get_context_data(context, 'may_fire', 'no') != 'no':
            return

        # Look up which branch_nodes have already completed.
        default   = dict([(repr(input.id), False) for input in self.inputs])
        completed = job.get_context_data(context, 'completed', default)

        # Make sure that the current notification is not a duplicate.
        assert completed[repr(branch_node.activity.id)] == False
        completed[repr(branch_node.activity.id)] = True

        # If all branch_nodes are now completed, reset the state.
        n_completed = completed.values().count(True)
        if n_completed == len(completed):
            job.set_context_data(context, completed = default)

        # If the threshold was reached, get ready to fire.
        if n_completed == len(completed) \
          or (self.threshold is not None and n_completed >= self.threshold):
            job.set_context_data(context, may_fire = 'yes')

            # If this is a cancelling join, cancel all incoming branches,
            # except for the one that just completed.
            if self.cancel:
                nodes = self.split_activity.get_activated_branch_nodes(job, branch_node)
                nodes.remove(start_node)
                for node in nodes:
                    node.cancel()

            return

        # Merge all except for the last branch_node.
        job.set_context_data(context, completed = completed)
        branch_node.drop_children()
        branch_node.set_status(COMPLETED)


    def completed_notify(self, job, branch_node):
        if self.split_activity is None:
            return self._completed_notify_unstructured(job, branch_node)
        return self._completed_notify_structured(job, branch_node)


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
            context = branch_node.find_path(None, self.split_activity)

        # Make sure that all inputs have completed.
        if job.get_context_data(context, 'may_fire', 'no') != 'yes':
            return False

        job.set_context_data(context, may_fire = 'done')
        return Activity.execute(self, job, branch_node)
