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
from Task       import Task
from Join       import Join

class ThreadMerge(Join):
    """
    This class represents a task for synchronizing branch_nodes that were
    previously split using a a ThreadSplit.
    It has two or more incoming branches and one or more outputs.
    """

    def __init__(self, parent, name, split_task, **kwargs):
        """
        Constructor.
        
        parent -- a reference to the parent (Task)
        name -- a name for the pattern (string)
        split_task -- the name of the task that was previously used to split
                      the branch_node
        kwargs -- may contain the following keys:
                      threshold -- an integer that specifies how many incoming
                      branches need to complete before the task triggers.
                      When the limit is reached, the task fires but still
                      expects all other branches to complete.
                      cancel -- when set to True, remaining incoming branches
                      are cancelled as soon as the discriminator is activated.
        """
        assert split_task is not None
        Join.__init__(self, parent, name, split_task, **kwargs)


    def _get_structured_context(self, branch_node):
        # In structured context, the context is the path up to the point where
        # the split happened.
        split_task = branch_node.job.get_task_from_name(self.split_task)
        split_node = branch_node.find_ancestor(split_task)
        return split_node.id


    def try_fire(self, branch_node):
        context = self._get_structured_context(branch_node)

        # If the threshold was already reached, there is nothing else to do.
        if branch_node.job.get_context_data(context, 'fired', 'no') == 'yes':
            branch_node.set_status(BranchNode.COMPLETED)
            return False

        # Retrieve a list of all activated branch_nodes from the associated
        # task that did the conditional parallel split.
        split_task = branch_node.job.get_task_from_name(self.split_task)
        split_node = branch_node.find_ancestor(split_task)
        nodes      = split_node.children

        # The default threshold is the number of threads that were started.
        threshold = self.threshold
        if self.threshold_attr is not None:
            threshold = branch_node.job.get_attribute(self.threshold_attr)
        if threshold is None:
            threshold = len(nodes)

        # Look up which branch_nodes have already completed.
        waiting_nodes = []
        completed     = 0
        for node in nodes:
            # Refresh path prediction.
            node.task.predict(node)

            if self._branch_is_complete(node):
                completed += 1
            else:
                waiting_nodes.append(node)

        # If the threshold was reached, get ready to fire.
        if completed >= threshold:
            branch_node.job.set_context_data(context, fired = 'yes')

            # If this is a cancelling join, cancel all incoming branches,
            # except for the one that just completed.
            if self.cancel:
                for node in waiting_nodes:
                    node.task.cancel(node)

            return True

        # We do NOT set the branch_node status to COMPLETED, because in
        # case all other incoming tasks get cancelled (or never reach
        # the ThreadMerge for other reasons, such as reaching a stub branch),
        # we need to revisit it.
        return False


    def _ready_to_proceed(self, branch_node):
        return self.try_fire(branch_node)


    def _execute(self, branch_node):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        context = self._get_structured_context(branch_node)
        branch_node.job.set_context_data(context, may_fire = 'done')

        # Mark all nodes in the same thread that reference this task as
        # COMPLETED.
        for node in branch_node.job.branch_tree:
            if node.thread_id != branch_node.thread_id:
                continue
            if node.task != self:
                continue
            node.state = BranchNode.COMPLETED
        return Task._execute(self, branch_node)
