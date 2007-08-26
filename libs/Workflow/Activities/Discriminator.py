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

class Discriminator(Activity):
    """
    Once the first of the inputs has completed, the output is activated.
    Completion of the other task is ignored and does not result in a second
    instance of the output task.

    This task has two or more inputs and one or more outputs.
    """

    def __init__(self, parent, name, split_activity, **kwargs):
        """
        Constructor.
        
        parent -- a reference to the parent (Activity)
        name -- a name for the pattern (string)
        split_activity -- the activity that was previously used to split the
                          branch_node
        """
        assert split_activity is not None
        self.cancel = kwargs.get('cancel', False)
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


    def completed_notify(self, job, branch_node):
        # The context is the path up to the point where the split happened.
        context = branch_node.find_path(None, self.split_activity)

        # If this is a cancelling discriminator, cancel all incoming branches,
        # except for the one that just completed.
        if self.cancel:
            nodes      = self.split_activity.get_activated_branch_nodes(job, branch_node)
            split_node = branch_node.find_ancestor(self.split_activity)
            start_node = branch_node.get_child_of(split_node)
            nodes.remove(start_node)
            for node in nodes:
                node.cancel()
            job.set_context_data(context, may_fire = True)
            return

        # Look up which inputs have already completed.
        default   = dict([(repr(i.id), False) for i in self.inputs])
        completed = job.get_context_data(context, 'completed', default)

        # Make sure that the current notification is not a duplicate.
        assert completed[repr(branch_node.activity.id)] == False
        completed[repr(branch_node.activity.id)] = True

        # If this is the first notification, activate, else discontinue the
        # branch_node.
        if completed.values().count(True) == 1:
            job.set_context_data(context, may_fire = True)
        else:
            branch_node.drop_children()
            branch_node.state = CANCELLED

        # If all branch_nodes are now completed, reset the state.
        if completed.values().count(False) == 0:
            completed = default

        job.set_context_data(context, completed = completed)


    def execute(self, job, branch_node):
        """
        Runs the activity. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        assert job         is not None
        assert branch_node is not None
        self.test()

        # The context is the path up to the point where the split happened.
        context = branch_node.find_path(None, self.split_activity)

        # Make sure that all inputs have completed.
        if job.get_context_data(context, 'may_fire', False) == False:
            return False
        job.set_context_data(context, may_fire = False)

        return Activity.execute(self, job, branch_node)
