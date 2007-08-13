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

class MultiInstance(Activity):
    """
    When executed, this activity performs a split on the current branch.
    The number of outgoing branches depends on the runtime value of a
    specified attribute.
    If more than one input is connected, the activity performs an implicit
    multi merge.

    This task has one or more inputs and may have any number of outputs.
    """

    def __init__(self, parent, name, attribute_name):
        """
        Constructor.
        
        parent -- a reference to the parent (Activity)
        name -- a name for the pattern (string)
        attribute_name -- the name of the attribute that specifies the number
                          of outgoing branches.
        """
        assert attribute_name is not None
        Activity.__init__(self, parent, name)
        self.attribute_name = attribute_name


    def get_activated_branches(self, job):
        """
        Returns the list of branches that were activated in the previous call
        of execute().
        """
        return job.get_context_data(self, 'activated_branches', [])


    def execute(self, job, branch):
        """
        Runs the activity. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        assert job    is not None
        assert branch is not None
        self.test()

        # Run user code, if any.
        if self.user_func is not None:
            self.user_func(job, branch, self)

        # Split.
        activated_branches = []
        split_n = job.get_attribute(self.attribute_name)
        for i in range(split_n):
            for output in self.outputs:
                new_branch = job.split_branch(branch)
                new_branch.queue_next_activity(output)
                output.completed_notify(job, new_branch, self)
                activated_branches.append(new_branch)

        # Store how many branches were activated, because
        # a subsequent structured merge may require the information.
        job.set_context_data(self, activated_branches = activated_branches)

        # Terminate the original branch.
        job.branch_completed_notify(branch)
        return False
