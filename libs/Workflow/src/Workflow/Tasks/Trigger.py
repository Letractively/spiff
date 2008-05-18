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
from Workflow.BranchNode import BranchNode
from Workflow.Exception  import WorkflowException
from Task                import Task

class Trigger(Task):
    """
    This class implements a task that triggers an event on another 
    task.
    If more than one input is connected, the task performs an implicit
    multi merge.
    If more than one output is connected, the task performs an implicit
    parallel split.
    """

    def __init__(self, parent, name, context, **kwargs):
        """
        Constructor.

        parent -- a reference to the parent (Task)
        name -- a name for the task (string)
        context -- a list of the names of tasks that are to be triggered
        """
        assert parent  is not None
        assert name    is not None
        assert context is not None
        assert type(context) == type([])
        Task.__init__(self, parent, name, **kwargs)
        self.context = context
        self.times   = kwargs.get('times', 1)
        self.queued  = 0


    def trigger(self, branch_node):
        """
        Enqueue a trigger, such that this tasks triggers mutliple times later
        when execute() is called.
        """
        self.queued += 1
        # All instances that have already completed need to be put into
        # WAITING again.
        for node in branch_node.job.branch_tree:
            if node.thread_id != branch_node.thread_id:
                continue
            if node.task == self and node.has_state(BranchNode.COMPLETED):
                node.state = BranchNode.WAITING


    def _execute(self, branch_node):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.

        branch_node -- the branch_node in which this method is executed
        """
        for i in range(self.times + self.queued):
            for task_name in self.context:
                task = branch_node.job.get_task_from_name(task_name)
                task.trigger(branch_node)
        self.queued = 0
        return Task._execute(self, branch_node)
