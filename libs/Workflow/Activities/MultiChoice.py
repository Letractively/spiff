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

class MultiChoice(Activity):
    """
    This class represents an if condition where multiple conditions may match
    at the same time, creating multiple branch_nodees.
    It has two or more inputs and two or more outputs.
    """
    EQUAL,          \
    NOT_EQUAL,      \
    LESS_THAN,      \
    GREATER_THAN,   \
    MATCHES         = range(5)

    def __init__(self, parent, name):
        """
        Constructor.
        
        parent -- a reference to the parent (Activity)
        name -- a name for the pattern (string)
        """
        Activity.__init__(self, parent, name)
        self.outputs          = []
        self.cond_activities  = []


    def connect(self, activity):
        """
        Convenience wrapper around connect_if() where condition is set to None.
        """
        return self.connect_if(None, activity)


    def connect_if(self, condition, activity):
        """
        Connects an activity that is executed if the condition DOES match.
        
        condition -- a tuple of (term1, operator, term2), where term1 and
                     term2 are attribute names, and operator is one of EQUAL,
                     NOT_EQUAL, LESS_THAN, GREATER_THAN, MATCHES.
        activity -- the following activity
        """
        assert activity is not None
        self.outputs.append(activity)
        self.cond_activities.append((condition, activity))
        activity.connect_notify(self)


    def get_activated_branch_nodes(self, job, branch_node):
        """
        Returns the list of branch_nodes that were activated in the previous call
        of execute().
        """
        context = branch_node.find_path(None, self)
        return job.get_context_data(context, 'activated_branch_nodes', [])


    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        Activity.test(self)
        if len(self.outputs) < 2:
            raise WorkflowException(self, 'At least two outputs required.')
        for condition, activity in self.cond_activities:
            if activity is None:
                raise WorkflowException(self, 'Condition with no activity.')
            if condition is None:
                continue
            elif condition[0] is None:
                raise WorkflowException(self, 'Term 1 not specified.')
            elif condition[1] is None:
                raise WorkflowException(self, 'Unknown operator.')
            elif condition[2] is None:
                raise WorkflowException(self, 'Term 2 not specified.')


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
            matches = False
            if condition is None:
                matches = True
            else:
                term1 = job.get_attribute(condition[0])
                term2 = job.get_attribute(condition[2])
                op    = condition[1]
                if op == self.EQUAL:
                    if term1 == term2:
                        matches = True
                elif op == self.NOT_EQUAL:
                    if term1 != term2:
                        matches = True
                elif op == self.LESS_THAN:
                    if int(term1) < int(term2):
                        matches = True
                elif op == self.GREATER_THAN:
                    if int(term1) > int(term2):
                        matches = True
                elif op == self.MATCHES:
                    if re.search(term2, term1):
                        matches = True
                else:
                    assert False  # Invalid operator.
            if not matches:
                continue

            # Create a new branch_node.
            new_branch_node = branch_node.add_child(output)
            output.completed_notify(job, branch_node, self)
            activated_branch_nodes.append(new_branch_node)

        # Store the info of how many branch_nodes were activated, because
        # a subsequent structured merge may require the information.
        context = branch_node.find_path(None, self)
        job.set_context_data(context, activated_branch_nodes = activated_branch_nodes)
        branch_node.activity_status_changed_notify(self, COMPLETED)

        return True
