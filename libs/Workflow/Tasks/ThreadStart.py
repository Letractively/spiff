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
from Exception import WorkflowException
from Task  import Task

class ThreadStart(Task):
    """
    This class implements the task the is placed at the beginning
    of each thread. It is NOT supposed to be used by in the API, it is
    used internally only (by the ThreadSplit task).
    The task has no inputs and at least one output.
    If more than one output is connected, the task does an implicit
    parallel split.
    """

    def __init__(self, parent):
        """
        Constructor.
        
        parent -- a reference to the parent (Task)
        """
        Task.__init__(self, parent, 'ThreadStart')
        self.internal = True


    def execute(self, job, branch_node):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        assert job    is not None
        assert branch_node is not None
        self.test()
        branch_node.assign_new_thread_id()
        return Task.execute(self, job, branch_node)
