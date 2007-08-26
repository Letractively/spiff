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


    def _branch_is_complete(self, branch_node):
        # Determine whether that branch is now completed by checking whether
        # it has any waiting items other than myself in it.
        for node in BranchNode.Iterator(branch_node, WAITING):
            if node.activity == self:
                continue
            return False
        return True


    def _may_fire(self, job, branch_node, context, branch_nodes, threshold):
        # If the threshold was already reached, there is nothing else to do.
        if job.get_context_data(context, 'fired', 'no') == 'yes':
            branch_node.set_status(COMPLETED)
            return False

        # Look up which branch_nodes have already completed.
        waiting_nodes = []
        completed     = 0
        for node in branch_nodes:
            if self._branch_is_complete(node):
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
        threshold = None
        if self.threshold is not None:
            threshold = self.threshold

        # Unstructured context.
        if self.split_activity is None:
            # Look at the tree to find all places where this activity is used.
            nodes = []
            for node in job.branch_tree:
                if node.activity != self:
                    continue
                nodes.append(node)

            if threshold is None:
                threshold = len(self.inputs)

            return self._may_fire(job, branch_node, self.id, nodes, threshold)

        # In structured context, the context is the path up to the point where
        # the split happened.
        context = branch_node.find_path(None, self.split_activity)

        # Retrieve a list of all activated branch_nodes from the associated
        # activity that did the conditional parallel split.
        nodes = self.split_activity.get_activated_branch_nodes(job, branch_node)

        if threshold is None:
            threshold = len(nodes)

        return self._may_fire(job, branch_node, context, nodes, threshold)


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
        if not self.may_fire(job, branch_node):
            return False

        job.set_context_data(context, may_fire = 'done')
        return Activity.execute(self, job, branch_node)
