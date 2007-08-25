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

class MultiInstance(Activity):
    """
    When executed, this activity performs a split on the current branch_node.
    The number of outgoing branch_nodes depends on the runtime value of a
    specified attribute.
    If more than one input is connected, the activity performs an implicit
    multi merge.

    This task has one or more inputs and may have any number of outputs.
    """

    def __init__(self, parent, name, attribute_name):
        """
        Constructor.
        
        parent -- a reference to the parent (Activity)
        name -- a name for the pattern (string)
        attribute_name -- the name of the attribute that specifies the number
                          of outgoing branch_nodes.
        """
        assert attribute_name is not None
        Activity.__init__(self, parent, name)
        self.attribute_name = attribute_name


    def get_activated_branch_nodes(self, job, branch_node):
        """
        Returns the list of branch_nodes that were activated in the previous call
        of execute().
        """
        context = branch_node.get_path(None, self)
        return job.get_context_data(context, 'activated_branch_nodes', [])


    def execute(self, job, branch_node):
        """
        Runs the activity. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        assert job    is not None
        assert branch_node is not None
        self.test()

        # Run user code, if any.
        if self.user_func is not None:
            self.user_func(job, branch_node, self)

        # Split.
        activated_branch_nodes = []
        split_n = job.get_attribute(self.attribute_name)
        for i in range(split_n):
            for output in self.outputs:
                new_branch_node = branch_node.add_child(output)
                output.completed_notify(job, branch_node, self)
                activated_branch_nodes.append(new_branch_node)

        # Store how many branch_nodes were activated, because
        # a subsequent structured merge may require the information.
        context = branch_node.get_path(None, self)
        job.set_context_data(context, activated_branch_nodes = activated_branch_nodes)

        branch_node.activity_status_changed_notify(self, COMPLETED)
        return False
