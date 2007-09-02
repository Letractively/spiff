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
import Tasks
from mutex      import mutex
from BranchNode import *

class Job(object):
    """
    This class implements the engine that executes a workflow.
    It is a essentially a facility for managing all branches.
    A Job is also the place that holds the attributes of a running workflow.
    """

    def __init__(self, workflow, **kwargs):
        """
        Constructor.
        """
        assert workflow is not None
        self.workflow         = workflow
        self.attributes       = {}
        self.context_data     = {}
        self.locks            = {}
        self.last_node        = None
        self.on_complete      = kwargs.get('on_complete',      None)
        self.on_complete_data = kwargs.get('on_complete_data', None)
        self.branch_tree      = BranchNode(self, Tasks.Task(workflow, 'Root'))
        self.success          = True

        # Prevent the root node from being executed.
        self.branch_tree.state = BranchNode.COMPLETED
        start = self.branch_tree.add_child(workflow.start)

        workflow.start.predict(self, start)
        #start.dump()


    def task_completed_notify(self, task):
        if self.on_complete is None:
            return
        state = BranchNode.WAITING | BranchNode.PREDICTED
        iter  = BranchNode.Iterator(self.branch_tree, state)
        try:
            next = iter.next()
            return
        except:
            # No waiting nodes found.
            self.on_complete(self, self.on_complete_data)


    def is_defined(self, name):
        """
        Returns True if an attribute with the given name exists, False
        otherwise.

        name -- an attribute name (string)
        """
        if self.attributes.has_key(name):
            return 1
        return 0


    def set_attribute(self, **kwargs):
        """
        Defines the given attribute/value pairs.
        """
        self.attributes.update(kwargs)


    def get_attribute(self, name, default = None):
        """
        Returns the value of the attribute with the given name, or the given
        default value if the attribute does not exist.

        name -- an attribute name (string)
        default -- the default value the be returned if the attribute does not
                   exist.
        """
        if self.attributes.has_key(name):
            return self.attributes[name]
        return default


    def get_mutex(self, name):
        if not self.locks.has_key(name):
            self.locks[name] = mutex()
        return self.locks[name]


    def set_context_data(self, context, *args, **kwargs):
        """
        Defines the given attribute/value pairs for the given context.

        context -- Specifies an identifier for the scope in which the data
                   is defined. You may also use an object as identifier.
        """
        if not self.context_data.has_key(repr(context)):
            self.context_data[repr(context)] = {}
        self.context_data[repr(context)].update(kwargs)


    def del_context_data(self, context, name = None):
        """
        Removes the data with the given name, or all data if no name was
        given.

        context -- Specifies an identifier for the scope in which the data
                   is deleted. You may also use an object as identifier.
        """
        if name is None:
            self.context_data[repr(context)] = {}
        elif self.context_data[repr(context)].has_key(name):
            del self.context_data[repr(context)][name]


    def get_context_data(self, context, name, default = None):
        """
        Returns the value of the data with the given name, or None if
        the attribute does not exist.

        context -- Specifies an identifier for the scope from which the data
                   is returned. You may also use an object as identifier.
        """
        if not self.context_data.has_key(repr(context)):
            return default
        if not self.context_data[repr(context)].has_key(name):
            return default
        return self.context_data[repr(context)][name]


    def cancel(self, success = False):
        """
        Cancels all open tasks in the job.

        success -- whether the Job should be marked as successfully completed
                   vs. unsuccessful
        """
        self.success = success
        cancel = []
        state  = BranchNode.WAITING | BranchNode.PREDICTED
        for node in BranchNode.Iterator(self.branch_tree, state):
            cancel.append(node)
        for node in cancel:
            node.cancel()
    

    def get_task_from_name(self, name):
        return self.workflow.tasks[name]


    def execute_next(self, pick_up = True):
        """
        Runs the next task.
        Returns True if completed, False otherwise.

        pick_up -- when True, this method attempts to choose the next task
                   not by searching beginning at the root, but by searching
                   from the position at which the last call of execute_next()
                   left off.
        """
        # Try to pick up where we left off.
        blacklist = []
        if pick_up and self.last_node is not None:
            try:
                iter = BranchNode.Iterator(self.last_node, BranchNode.WAITING)
                next = iter.next()
            except:
                next = None
            self.last_node = None
            if next is not None:
                if next.task.execute(next):
                    self.last_node = next
                    return True
                blacklist.append(next)

        # Walk through all waiting tasks.
        for node in BranchNode.Iterator(self.branch_tree, BranchNode.WAITING):
            for blacklisted_node in blacklist:
                if node.is_descendant_of(blacklisted_node):
                    continue
            if not node.task.execute(node):
                blacklist.append(node)
                continue
            self.last_node = node
            return True
        return False


    def execute_all(self, pick_up = True):
        """
        Runs all branches until completion.
        """
        while self.execute_next(pick_up):
            pass
