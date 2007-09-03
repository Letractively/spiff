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

class Join(Task):
    """
    This class represents a task for synchronizing branch_nodes that were
    previously split using a conditional task, such as MultiChoice.
    It has two or more incoming branches and one or more outputs.
    """

    def __init__(self, parent, name, split_task = None, **kwargs):
        """
        Constructor.
        
        parent -- a reference to the parent (Task)
        name -- a name for the pattern (string)
        split_task -- the task that was previously used to split the
                          branch_node
        kwargs -- may contain the following keys:
                      threshold -- an integer that specifies how many incoming
                      branches need to complete before the task triggers.
                      When the limit is reached, the task fires but still
                      expects all other branches to complete.
                      threshold_attribute -- like threshold, but the value is
                      read from the attribute with the given name at runtime.
                      cancel -- when set to True, remaining incoming branches
                      are cancelled as soon as the discriminator is activated.
        """
        assert not (kwargs.has_key('threshold') \
                and kwargs.has_key('threshold_attribute'))
        Task.__init__(self, parent, name, **kwargs)
        self.split_task       = split_task
        self.threshold        = kwargs.get('threshold',           None)
        self.threshold_attr   = kwargs.get('threshold_attribute', None)
        self.cancel_remaining = kwargs.get('cancel',              False)


    def _branch_is_complete(self, branch_node):
        # Determine whether that branch is now completed by checking whether
        # it has any waiting items other than myself in it.
        state = BranchNode.WAITING | BranchNode.PREDICTED
        skip  = None
        for node in BranchNode.Iterator(branch_node, state):
            # If the current node is a child of myself, ignore it.
            if skip is not None and node.is_descendant_of(skip):
                continue
            if node.task == self:
                skip = node
                continue
            return False
        return True


    def _branch_may_merge_at(self, branch_node):
        for node in branch_node:
            # Ignore nodes that were created by a trigger.
            if node.state & BranchNode.TRIGGERED != 0:
                continue
            # Merge found.
            if node.task == self:
                return True
            # If the node is predicted with less outputs than he has
            # children, that means the prediction may be incomplete (for
            # example, because a prediction is not yet possible at this time).
            if node.state & BranchNode.PREDICTED != 0 \
                and len(node.task.outputs) > len(node.children):
                return True
        return False


    def _get_structured_context(self, branch_node):
        split_task = branch_node.job.get_task_from_name(self.split_task)
        split_node = branch_node.find_ancestor(split_task)
        start_node = branch_node.find_child_of(split_task)
        return '%s(%s)' % (split_node.id, start_node.thread_id)


    def _get_unstructured_context(self, branch_node):
        return '%s(%s)' % (self.id, branch_node.thread_id)


    def _fire(self, branch_node, waiting_nodes):
        """
        Fire, and cancel remaining tasks, if so requested.
        """
        if self.split_task is None:
            context = self._get_unstructured_context(branch_node)
        else:
            context = self._get_structured_context(branch_node)

        branch_node.job.set_context_data(context, fired = 'ready')

        # If this is a cancelling join, cancel all incoming branches,
        # except for the one that just completed.
        if self.cancel_remaining:
            for node in waiting_nodes:
                node.task.cancel(node)


    def _try_fire_unstructured(self, branch_node, force = False):
        # If the threshold was already reached, there is nothing else to do.
        context = self._get_unstructured_context(branch_node)
        if branch_node.job.get_context_data(context, 'fired', 'no') == 'yes':
            branch_node.set_status(BranchNode.COMPLETED)
            return False
        if branch_node.job.get_context_data(context, 'fired', 'no') == 'ready':
            branch_node.set_status(BranchNode.COMPLETED)
            return True

        # The default threshold is the number of inputs.
        threshold = self.threshold
        if self.threshold_attr is not None:
            threshold = branch_node.job.get_attribute(self.threshold_attr)
        if threshold is None:
            threshold = len(self.inputs)

        # Look at the tree to find all places where this task is used.
        nodes = []
        for task in self.inputs:
            for node in branch_node.job.branch_tree:
                if node.thread_id != branch_node.thread_id:
                    continue
                if node.task != task:
                    continue
                nodes.append(node)

        # Look up which branch_nodes have already completed.
        waiting_nodes = []
        completed     = 0
        for node in nodes:
            if node.parent is None or node.state & BranchNode.COMPLETED != 0:
                completed += 1
            else:
                waiting_nodes.append(node)

        # If the threshold was reached, get ready to fire.
        if force or completed >= threshold:
            self._fire(branch_node, waiting_nodes)
            return True

        # We do NOT set the branch_node status to COMPLETED, because in
        # case all other incoming tasks get cancelled (or never reach
        # the Join for other reasons, such as reaching a stub branch), we
        # need to revisit it.
        return False


    def _try_fire_structured(self, branch_node, force = False):
        # In structured context, the context is the path up to the point where
        # the split happened.
        context = self._get_structured_context(branch_node)

        # If the threshold was already reached, there is nothing else to do.
        if branch_node.job.get_context_data(context, 'fired', 'no') == 'yes':
            branch_node.set_status(BranchNode.COMPLETED)
            return False
        if branch_node.job.get_context_data(context, 'fired', 'no') == 'ready':
            branch_node.set_status(BranchNode.COMPLETED)
            return True

        # Retrieve a list of all activated branch_nodes from the associated
        # task that did the conditional parallel split.
        split_task = branch_node.job.get_task_from_name(self.split_task)
        nodes      = split_task.get_activated_branch_nodes(branch_node)

        # The default threshold is the number of branches that were started.
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

            if not self._branch_may_merge_at(node):
                completed += 1
            elif self._branch_is_complete(node):
                completed += 1
            else:
                waiting_nodes.append(node)

        # If the threshold was reached, get ready to fire.
        if force or completed >= threshold:
            self._fire(branch_node, waiting_nodes)
            return True

        # We do NOT set the branch_node status to COMPLETED, because in
        # case all other incoming tasks get cancelled (or never reach
        # the Join for other reasons, such as reaching a stub branch), we
        # need to revisit it.
        return False


    def try_fire(self, branch_node, force = False):
        if self.split_task is None:
            return self._try_fire_unstructured(branch_node, force)
        return self._try_fire_structured(branch_node, force)


    def trigger(self, branch_node):
        """
        May be called to fire the Join before the incoming branches are
        completed.
        """
        for node in branch_node.job.branch_tree:
            if node.thread_id != branch_node.thread_id:
                continue
            if node.task != self:
                continue
            self.try_fire(node, True)


    def _ready_to_proceed(self, branch_node):
        return self.try_fire(branch_node)


    def _execute(self, branch_node):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        if self.split_task is None:
            context = self._get_unstructured_context(branch_node)
        else:
            context = self._get_structured_context(branch_node)
        branch_node.job.set_context_data(context, fired = 'yes')

        # Mark all nodes in the same thread that reference this task as
        # COMPLETED.
        for node in branch_node.job.branch_tree:
            if node.state & BranchNode.PREDICTED != 0:
                continue
            if node.thread_id != branch_node.thread_id:
                continue
            if node.task != self:
                continue
            node.state = BranchNode.COMPLETED
        return Task._execute(self, branch_node)
