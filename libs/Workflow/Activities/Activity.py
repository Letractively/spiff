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

class Activity(object):
    """
    This class implements a activity with one or more inputs and
    one or more outputs.
    If more than one input is connected, the activity performs an implicit
    multi merge.
    If more than one output is connected, the activity performs an implicit
    parallel split.
    """

    def __init__(self, parent, name):
        """
        Constructor.

        parent -- a reference to the parent (Activity)
        name -- a name for the activity (string)
        """
        assert parent is not None
        assert name   is not None
        self._parent   = parent
        self.id        = None
        self.name      = name
        self.inputs    = []
        self.outputs   = []
        self.user_func = None
        self.manual    = False
        self._parent.add_notify(self)
        assert self.id is not None


    def connect(self, activity):
        """
        Connect the *following* activity to this one. In other words, the
        given activity is added as an output activity.

        activity -- the activity to connect to.
        """
        self.outputs.append(activity)
        activity.connect_notify(self)


    def connect_notify(self, activity):
        """
        Called by the previous activity to let us know that it exists.

        activity -- the activity by which this method is executed
        """
        self.inputs.append(activity)


    def completed_notify(self, job, branch_node):
        """
        Called by the previous activity to let us know that it has finished.

        job -- the job in which this method is executed
        branch_node -- the branch_node in which this method is executed
        """
        pass


    def get_activated_branch_nodes(self, job, branch_node):
        """
        Returns the list of branch_nodes that were activated in the previous call
        of execute().

        job -- the job in which this method is executed
        branch_node -- the branch_node in which this method is executed
        """
        context = branch_node.find_path(None, self)
        return job.get_context_data(context, 'activated_branch_nodes', [])


    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        if self.id is None:
            raise WorkflowException(self, 'Activity is not yet instanciated.')
        if len(self.inputs) < 1:
            raise WorkflowException(self, 'No input activity connected.')
        elif len(self.outputs) < 1:
            raise WorkflowException(self, 'No output activity connected.')


    def execute(self, job, branch_node):
        """
        Runs the activity. Should not be called directly.
        Returns True if completed, False otherwise.

        job -- the job in which this method is executed
        branch_node -- the branch_node in which this method is executed
        """
        assert job         is not None
        assert branch_node is not None
        self.test()

        # Run user code, if any.
        if self.user_func is not None:
            self.user_func(job, branch_node, self)

        # If we have more than one output, implicitly split.
        activated_branch_nodes = []
        for output in self.outputs:
            new_branch_node = branch_node.add_child(output)
            output.completed_notify(job, branch_node)
            activated_branch_nodes.append(new_branch_node)

        # Store the info of how many branch_nodes were activated, because
        # a subsequent structured merge may require the information.
        context = branch_node.find_path(None, self)
        job.set_context_data(context, activated_branch_nodes = activated_branch_nodes)
        branch_node.set_status(COMPLETED)
        return True
