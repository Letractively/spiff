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
from BranchNode  import *
from Exception   import WorkflowException
from Task        import Task
from ThreadStart import ThreadStart

class ThreadSplit(Task):
    """
    When executed, this task performs a split on the current branch_node.
    The number of outgoing branch_nodes depends on the runtime value of a
    specified attribute.
    If more than one input is connected, the task performs an implicit
    multi merge.

    This task has one or more inputs and may have any number of outputs.
    """

    def __init__(self, parent, name, **kwargs):
        """
        Constructor.
        
        parent -- a reference to the parent (Task)
        name -- a name for the pattern (string)
        kwargs -- must contain one of the following:
                    times -- the number of instances to create.
                    times-attribute -- the name of the attribute that
                                       specifies the number of outgoing
                                       instances.
        """
        assert kwargs.has_key('times_attribute') or kwargs.has_key('times')
        Task.__init__(self, parent, name, **kwargs)
        self.times_attribute = kwargs.get('times_attribute', None)
        self.times           = kwargs.get('times',           None)
        self.thread_starter  = ThreadStart(parent, **kwargs)
        self.outputs.append(self.thread_starter)
        self.thread_starter.connect_notify(self)


    def connect(self, task):
        """
        Connect the *following* task to this one. In other words, the
        given task is added as an output task.

        task -- the task to connect to.
        """
        self.thread_starter.outputs.append(task)
        task.connect_notify(self.thread_starter)


    def _find_my_branch_node(self, job):
        for node in job.branch_tree:
            if node.thread_id != branch_node.thread_id:
                continue
            if node.task == self:
                return node
        return None


    def get_activated_branch_nodes(self, branch_node):
        """
        Returns the list of branch_nodes that were activated in the previous call
        of execute().

        branch_node -- the branch_node in which this method is executed
        """
        return self.thread_starter.get_activated_branch_nodes(branch_node)


    def trigger(self, branch_node):
        """
        May be called after execute() was already completed to create an
        additional outbound instance.
        """
        # Find a BranchNode for this task.
        my_branch_node = self._find_my_branch_node(branch_node.job)
        for output in self.outputs:
            state           = BranchNode.WAITING | BranchNode.TRIGGERED
            new_branch_node = my_branch_node.add_child(output, state)


    def _predict(self, branch_node):
        # Since the attribute value might have changed by the time a future
        # task calls this method, we store the number of splits in the
        # context data.
        split_n = branch_node.job.get_context_data('split_n', self.times)
        if split_n is None:
            split_n = branch_node.job.get_attribute(self.times_attribute, 1)

        # Predict the outputs.
        outputs = []
        for i in range(split_n):
            outputs.append(self.thread_starter)
        branch_node.update_children(outputs, BranchNode.PREDICTED)


    def _execute(self, branch_node):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        # Split, and remember the number of splits in the context data.
        split_n = self.times
        if split_n is None:
            split_n = branch_node.job.get_attribute(self.times_attribute)
        branch_node.job.set_context_data(branch_node.id, split_n = split_n)

        # Create the outgoing nodes.
        outputs = []
        for i in range(split_n):
            outputs.append(self.thread_starter)
        branch_node.update_children(outputs)
        return True
