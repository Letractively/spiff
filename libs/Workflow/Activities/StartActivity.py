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
from Activity  import Activity

class StartActivity(Activity):
    """
    This class implements the activity the is placed at the beginning
    of each workflow. The activity has no inputs and at least one output.
    If more than one output is connected, the activity does an implicit
    parallel split.
    """

    def __init__(self, parent):
        """
        Constructor.
        
        parent -- a reference to the parent (Activity)
        """
        Activity.__init__(self, parent, 'Start')


    def connect_notify(self, activity):
        """
        Called by the previous activity to let us know that it exists.
        """
        raise WorkflowException(self, 'StartActivity can not have any inputs.')


    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        if len(self.inputs) != 0:
            raise WorkflowException(self, 'StartActivity with an input.')
        elif len(self.outputs) < 1:
            raise WorkflowException(self, 'No output activity connected.')
