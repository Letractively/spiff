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
from BranchNode import *
from Exception  import WorkflowException
from Activity   import Activity

class Condition(object):
    EQUAL,          \
    NOT_EQUAL,      \
    LESS_THAN,      \
    GREATER_THAN,   \
    MATCHES         = range(5)

    def __init__(self, op, **kwargs):
        """
        Constructor.

        op -- one of EQUAL, NOT_EQUAL, LESS_THAN, GREATER_THAN, MATCHES.
        kwargs -- must contain one of left_attribute/left and one of
                  right_attribute/right.
        """
        assert op is not None
        assert kwargs.has_key('left_attribute') or kwargs.has_key('left')
        assert kwargs.has_key('right_attribute') or kwargs.has_key('right')
        self.op = op
        self.left_attribute  = kwargs.get('left_attribute',  None)
        self.left            = kwargs.get('left',            None)
        self.right_attribute = kwargs.get('right_attribute', None)
        self.right           = kwargs.get('right',           None)

    def matches(self, job):
        # Fetch the value of the left and right expression.
        if self.left is not None:
            left = self.left
        else:
            left = job.get_attribute(self.left_attribute)
        if self.right is not None:
            right = self.right
        else:
            right = job.get_attribute(self.right_attribute)

        # Compare according to the operator.
        if self.op == self.EQUAL:
            if unicode(left) == unicode(right):
                return True
        elif self.op == self.NOT_EQUAL:
            if unicode(left) != unicode(right):
                return True
        elif self.op == self.LESS_THAN:
            if int(left) < int(right):
                return True
        elif self.op == self.GREATER_THAN:
            if int(left) > int(right):
                return True
        elif self.op == self.MATCHES:
            if re.search(right, left):
                return True
        else:
            assert False  # Invalid operator.
        return False

class MultiChoice(Activity):
    """
    This class represents an if condition where multiple conditions may match
    at the same time, creating multiple branch_nodees.
    This task has one or more inputs, and one or more incoming branches.
    This task has one or more outputs.
    """

    def __init__(self, parent, name):
        """
        Constructor.
        
        parent -- a reference to the parent (Activity)
        name -- a name for the pattern (string)
        """
        Activity.__init__(self, parent, name)
        self.cond_activities  = []


    def connect(self, activity):
        """
        Convenience wrapper around connect_if() where condition is set to None.
        """
        return self.connect_if(None, activity)


    def connect_if(self, condition, activity):
        """
        Connects an activity that is executed if the condition DOES match.
        
        condition -- a condition (Condition)
        activity -- the conditional activity
        """
        assert activity is not None
        self.outputs.append(activity)
        self.cond_activities.append((condition, activity))
        activity.connect_notify(self)


    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        Activity.test(self)
        if len(self.cond_activities) < 1:
            raise WorkflowException(self, 'At least one output required.')
        for condition, activity in self.cond_activities:
            if activity is None:
                raise WorkflowException(self, 'Condition with no activity.')
            if condition is None:
                continue
            if condition is None:
                raise WorkflowException(self, 'Condition is None.')


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

        # Find all matching conditions.
        activated_branch_nodes = []
        for condition, output in self.cond_activities:
            if condition is not None and not condition.matches(job):
                continue

            # Create a new branch_node.
            new_branch_node = branch_node.add_child(output)
            activated_branch_nodes.append(new_branch_node)

        # Store the info of how many branch_nodes were activated, because
        # a subsequent structured merge may require the information.
        context = branch_node.find_path(None, self)
        job.set_context_data(context, activated_branch_nodes = activated_branch_nodes)
        branch_node.set_status(COMPLETED)
        return True
