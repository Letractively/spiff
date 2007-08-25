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
    This class represents an exclusive choice (an if condition) activity
    where precisely one outgoing branch_node is selected. If none of the
    given condition matches, a default activity is selected.
    It has two or more inputs and two or more outputs.
    """
    def __init__(self, parent, name):
        """
        Constructor.
        
        parent -- a reference to the parent (Activity)
        name -- a name for the pattern (string)
        """
        MultiChoice.__init__(self, parent, name)
        self.default_activity = None


    def connect(self, activity):
        """
        Connects the activity that is executed if no other condition matches.

        activity -- the following activity
        """
        assert self.default_activity is None
        self.outputs.append(activity)
        self.default_activity = activity
        activity.connect_notify(self)


    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        MultiChoice.test(self)
        if self.default_activity is None:
            raise WorkflowException(self, 'A default output is required.')


    def execute(self, job, branch_node):
        """
        Runs the activity. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        assert job is not None
        assert branch_node is not None
        self.test()

        # Run user code, if any.
        if self.user_func is not None:
            self.user_func(job, branch_node, self)

        # Find the first matching condition.
        output = self.default_activity
        for condition, activity in self.cond_activities:
            if condition is None:
                output = activity
                break

            term1 = job.get_attribute(condition[0])
            term2 = job.get_attribute(condition[2])
            op    = condition[1]
            if op == self.EQUAL:
                if term1 == term2:
                    output = activity
                    break
            elif op == self.NOT_EQUAL:
                if term1 != term2:
                    output = activity
                    break
            elif op == self.LESS_THAN:
                if int(term1) < int(term2):
                    output = activity
                    break
            elif op == self.GREATER_THAN:
                if int(term1) > int(term2):
                    output = activity
                    break
            elif op == self.MATCHES:
                if re.search(term2, term1):
                    output = activity
                    break
            else:
                assert False  # Invalid operator.

        new_branch_node = branch_node.add_child(output)
        output.completed_notify(job, branch_node, self)
        branch_node.activity_status_changed_notify(self, COMPLETED)
        return True
