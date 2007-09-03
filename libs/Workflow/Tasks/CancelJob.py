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

class CancelJob(Task):
    """
    This class implements a trigger that cancels another task (branch).
    If more than one input is connected, the task performs an implicit
    multi merge.
    If more than one output is connected, the task performs an implicit
    parallel split.
    """

    def __init__(self, parent, name, **kwargs):
        """
        Constructor.

        parent -- a reference to the parent (Task)
        name -- a name for the task (string)
        kwargs -- may contain the following keys:
                  lock -- a list of locks that is aquired on entry of
                  execute() and released on leave of execute().
                  pre_assign -- a list of attribute name/value pairs
                  post_assign -- a list of attribute name/value pairs
        """
        Task.__init__(self, parent, name, **kwargs)
        self.cancel_successfully = kwargs.get('success', False)


    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        Task.test(self)
        if len(self.outputs) > 0:
            raise WorkflowException(self, 'CancelJob with an output.')


    def _execute(self, branch_node):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.

        branch_node -- the branch_node in which this method is executed
        """
        branch_node.job.cancel(self.cancel_successfully)
        return Task._execute(self, branch_node)
