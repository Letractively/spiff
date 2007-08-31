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

class StubTask(Task):
    """
    This class implements the task that is placed at the end of each
    workflow. It has one or more inputs and no outputs.
    If more than one input is connected, the task does an implicit
    simple merge.
    """

    def __init__(self, parent, name):
        """
        Constructor.
        
        parent -- a reference to the parent (Task)
        name -- a name for the pattern (string)
        """
        Task.__init__(self, parent, name)


    def connect(self, task):
        """
        Connect the *following* task to this one. In other words, the
        given task is added as an output task.
        """
        raise WorkflowException(self, 'StubTask can not have any outputs.')


    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        if len(self.inputs) < 1:
            raise WorkflowException(self, 'No input task connected.')
        elif len(self.outputs) != 0:
            raise WorkflowException(self, 'StubTask with an output.')
