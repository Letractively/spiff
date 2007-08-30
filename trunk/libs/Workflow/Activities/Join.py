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
                      threshold_attribute -- like threshold, but the value is
                      read from the attribute with the given name at runtime.
                      cancel -- when set to True, remaining incoming branches
                      are cancelled as soon as the discriminator is activated.
        """
        assert not (kwargs.has_key('threshold') \
                and kwargs.has_key('threshold_attribute'))
        Activity.__init__(self, parent, name)
        self.split_activity = split_activity
        self.threshold      = kwargs.get('threshold',           None)
        self.threshold_attr = kwargs.get('threshold_attribute', None)
        self.cancel         = kwargs.get('cancel',              False)


    def _branch_is_complete(self, job, branch_node):
        # Determine whether that branch is now completed by checking whether
        # it has any waiting items other than myself in it.
        state = BranchNode.WAITING | BranchNode.PREDICTED
        skip  = None
        for node in BranchNode.Iterator(branch_node, state):
            # If the current node is a child of myself, ignore it.
            if skip is not None and node.is_descendant_of(skip):
                continue
            if node.activity == self:
                skip = node
                continue
            return False
        return True


    def _branch_may_merge_at(self, job, branch_node):
        for node in branch_node:
            # Ignore nodes that were created by a trigger.
            if node.state & BranchNode.TRIGGERED != 0:
                continue
            # Merge found.
            if node.activity == self:
                return True
            # If the node has outputs even though it is predicted with no
            # children, that means the prediction may be incomplete (for
            # example, because a prediction is not yet possible at this time).
            if node.state & BranchNode.PREDICTED != 0 \
                and len(node.children) == 0           \
                and len(node.activity.outputs) > 0:
                return True
        return False


    def _get_structured_context(self, job, branch_node):
        path       = branch_node.find_path(None, self.split_activity)
        split_node = branch_node.find_child_of(self.split_activity)
        return '%s(%s)' % (path, split_node.thread_id)


    def _may_fire_unstructured(self, job, branch_node):
        # If the threshold was already reached, there is nothing else to do.
        context = '%s(%s)' % (self.id, branch_node.thread_id)
        if job.get_context_data(context, 'fired', 'no') == 'yes':
            branch_node.set_status(BranchNode.COMPLETED)
            return False

        # The default threshold is the number of inputs.
        threshold = self.threshold
        if self.threshold_attr is not None:
            threshold = job.get_attribute(self.threshold_attr)
        if threshold is None:
            threshold = len(self.inputs)

        # Look at the tree to find all places where this activity is used.
        nodes = []
        for activity in self.inputs:
            for node in job.branch_tree:
                if node.thread_id != branch_node.thread_id:
                    continue
                if node.activity != activity:
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
        if completed >= threshold:
            job.set_context_data(context, fired = 'yes')

            # If this is a cancelling join, cancel all incoming branches,
            # except for the one that just completed.
            if self.cancel:
                for node in waiting_nodes:
                    node.cancel()

            return True

        # We do NOT set the branch_node status to COMPLETED, because in
        # case all other incoming activities get cancelled (or never reach
        # the Join for other reasons, such as reaching a StubActivity), we
        # need to revisit it.
        return False


    def _may_fire_structured(self, job, branch_node):
        # In structured context, the context is the path up to the point where
        # the split happened.
        context = self._get_structured_context(job, branch_node)

        # If the threshold was already reached, there is nothing else to do.
        if job.get_context_data(context, 'fired', 'no') == 'yes':
            branch_node.set_status(BranchNode.COMPLETED)
            return False

        # Retrieve a list of all activated branch_nodes from the associated
        # activity that did the conditional parallel split.
        nodes = self.split_activity.get_activated_branch_nodes(job, branch_node)

        # The default threshold is the number of branches that were started.
        threshold = self.threshold
        if self.threshold_attr is not None:
            threshold = job.get_attribute(self.threshold_attr)
        if threshold is None:
            threshold = len(nodes)

        # Look up which branch_nodes have already completed.
        waiting_nodes = []
        completed     = 0
        for node in nodes:
            # Refresh path prediction.
            node.activity.predict(job, node)

            if not self._branch_may_merge_at(job, node):
                completed += 1
            elif self._branch_is_complete(job, node):
                completed += 1
            else:
                waiting_nodes.append(node)

        # If the threshold was reached, get ready to fire.
        if completed >= threshold:
            job.set_context_data(context, fired = 'yes')

            # If this is a cancelling join, cancel all incoming branches,
            # except for the one that just completed.
            if self.cancel:
                for node in waiting_nodes:
                    node.cancel()

            return True

        # We do NOT set the branch_node status to COMPLETED, because in
        # case all other incoming activities get cancelled (or never reach
        # the Join for other reasons, such as reaching a StubActivity), we
        # need to revisit it.
        return False


    def may_fire(self, job, branch_node):
        if self.split_activity is None:
            return self._may_fire_unstructured(job, branch_node)
        return self._may_fire_structured(job, branch_node)


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
            context = '%s(%s)' % (self.id, branch_node.thread_id)
        else:
            context = self._get_structured_context(job, branch_node)

        # Make sure that all inputs have completed.
        if not self.may_fire(job, branch_node):
            return False
        job.set_context_data(context, may_fire = 'done')

        # Mark all nodes in the same thread that reference this activity as
        # COMPLETED.
        for node in job.branch_tree:
            if node.thread_id != branch_node.thread_id:
                continue
            if node.activity != self:
                continue
            node.state = BranchNode.COMPLETED
        return Activity.execute(self, job, branch_node)
