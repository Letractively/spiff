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

    def __init__(self, parent, name, **kwargs):
        """
        Constructor.
        
        parent -- a reference to the parent (Activity)
        name -- a name for the pattern (string)
        kwargs -- must contain one of the following:
                    times -- the number of instances to create.
                    times-attribute -- the name of the attribute that
                                       specifies the number of outgoing
                                       instances.
        """
        assert kwargs.has_key('times_attribute') or kwargs.has_key('times')
        Activity.__init__(self, parent, name)
        self.times_attribute = kwargs.get('times_attribute', None)
        self.times           = kwargs.get('times',           None)


    def add_instance(self, job, branch_node):
        """
        May be called after execute() was already completed to create an
        additional outbound instance.
        """
        context        = branch_node.find_path(None, self)
        my_branch_node = branch_node.find_ancestor(self)
        activated_branch_nodes = job.get_context_data(context, 'activated_branch_nodes', [])
        for output in self.outputs:
            new_branch_node = my_branch_node.add_child(output)
            activated_branch_nodes.append(new_branch_node)
        job.set_context_data(context, activated_branch_nodes = activated_branch_nodes)


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
        split_n = self.times
        if split_n is None:
            split_n = job.get_attribute(self.times_attribute)
        for i in range(split_n):
            for output in self.outputs:
                new_branch_node = branch_node.add_child(output)
                activated_branch_nodes.append(new_branch_node)

        # Store how many branch_nodes were activated, because
        # a subsequent structured merge may require the information.
        context = branch_node.find_path(None, self)
        job.set_context_data(context, activated_branch_nodes = activated_branch_nodes)

        branch_node.set_status(COMPLETED)
        return True
