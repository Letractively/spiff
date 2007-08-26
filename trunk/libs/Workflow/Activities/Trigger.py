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

class Trigger(Activity):
    """
    This class implements an activity that triggers an event on another 
    activity.
    If more than one input is connected, the activity performs an implicit
    multi merge.
    If more than one output is connected, the activity performs an implicit
    parallel split.
    """

    def __init__(self, parent, name, context):
        """
        Constructor.

        parent -- a reference to the parent (Activity)
        name -- a name for the activity (string)
        context -- the MultiInstance activity that is instructed to create
                   another instance.
        """
        assert parent  is not None
        assert name    is not None
        assert context is not None
        Activity.__init__(self, parent, name)
        self.context = context


    def execute(self, job, branch_node):
        """
        Runs the activity. Should not be called directly.
        Returns True if completed, False otherwise.

        job -- the job in which this method is executed
        branch_node -- the branch_node in which this method is executed
        """
        assert job         is not None
        assert branch_node is not None
        self.test()

        self.context.trigger(job, branch_node)

        return Activity.execute(self, job, branch_node)
