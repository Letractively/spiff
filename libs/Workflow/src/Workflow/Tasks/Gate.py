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

class Gate(Task):
    """
    This class implements a task that can only execute when another
    specified task is completed.
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
        context -- the name of the task that needs to complete before this
                   task can execute.
        """
        assert parent  is not None
        assert name    is not None
        assert context is not None
        Task.__init__(self, parent, name, **kwargs)
        self.context = context


    def _ready_to_proceed(self, branch_node):
        task      = branch_node.job.get_task_from_name(self.context)
        root_node = branch_node.job.branch_tree
        for node in BranchNode.Iterator(root_node, BranchNode.COMPLETED):
            if node.thread_id != branch_node.thread_id:
                continue
            if node.task == task:
                return True
        return False


    def _execute(self, branch_node):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.

        branch_node -- the branch_node in which this method is executed
        """
        return Task._execute(self, branch_node)
