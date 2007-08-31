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
import re
from BranchNode  import *
from Exception   import WorkflowException
from MultiChoice import MultiChoice

class ExclusiveChoice(MultiChoice):
    """
    This class represents an exclusive choice (an if condition) task
    where precisely one outgoing branch_node is selected. If none of the
    given condition matches, a default task is selected.
    It has one or more inputs and two or more outputs.
    """
    def __init__(self, parent, name):
        """
        Constructor.
        
        parent -- a reference to the parent (Task)
        name -- a name for the pattern (string)
        """
        MultiChoice.__init__(self, parent, name)
        self.default_task = None


    def connect(self, task):
        """
        Connects the task that is executed if no other condition matches.

        task -- the following task
        """
        assert self.default_task is None
        self.outputs.append(task)
        self.default_task = task
        task.connect_notify(self)


    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        MultiChoice.test(self)
        if self.default_task is None:
            raise WorkflowException(self, 'A default output is required.')


    def execute(self, job, branch_node):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        assert job is not None
        assert branch_node is not None
        self.test()

        # Run user code, if any.
        if self.user_func is not None:
            self.user_func(job, branch_node, self)

        # Find the first matching condition.
        output = self.default_task
        for condition, task in self.cond_tasks:
            if condition is None or condition.matches(job):
                output = task
                break

        branch_node.update_children(output)
        branch_node.set_status(BranchNode.COMPLETED)
        return True
