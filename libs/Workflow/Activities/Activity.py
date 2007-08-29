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
from AbstractMethod import AbstractMethod
from BranchNode     import *
from Exception      import WorkflowException

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
        self.internal  = False  # Only for easing debugging.
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


    def get_activated_branch_nodes(self, job, branch_node):
        """
        Returns the list of branch_nodes that were activated in the previous call
        of execute().

        job -- the job in which this method is executed
        branch_node -- the branch_node in which this method is executed
        """
        my_branch_node = branch_node.find_ancestor(self)
        return my_branch_node.children


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


    def trigger(self, job, branch_node):
        """
        May be called by another activity to trigger an activity-specific
        event.
        """
        AbstractMethod()


    def predict(self, job, branch_node, seen = None):
        """
        Updates the branch such that all possible future routes are added
        with the PREDICTED flag.

        Should NOT be overwritten! Instead, overwrite the hook (_predict).
        """
        if seen is None:
            seen = []
        elif self in seen:
            return
        if branch_node.state & BranchNode.PREDICTED != 0:
            seen.append(self)
        if branch_node.state & BranchNode.COMPLETED == 0 \
            and branch_node.state & BranchNode.CANCELLED == 0:
            self._predict(job, branch_node)
        for node in branch_node.children:
            node.activity.predict(job, node, seen)


    def _predict(self, job, branch_node):
        branch_node.update_children(self.outputs, BranchNode.PREDICTED)


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
        branch_node.update_children(self.outputs)
        branch_node.set_status(BranchNode.COMPLETED)
        return True
