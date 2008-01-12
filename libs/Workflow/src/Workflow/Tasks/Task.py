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

class Assign(object):
    def __init__(self, left_attribute, **kwargs):
        """
        Constructor.

        kwargs -- must contain one of right_attribute/right.
        """
        assert left_attribute is not None
        assert kwargs.has_key('right_attribute') or kwargs.has_key('right')
        self.left_attribute  = left_attribute
        self.right_attribute = kwargs.get('right_attribute', None)
        self.right           = kwargs.get('right',           None)

    def assign(self, from_job, to_job):
        # Fetch the value of the right expression.
        if self.right is not None:
            right = self.right
        else:
            right = from_job.get_attribute(self.right_attribute)
        to_job.set_attribute(**{str(self.left_attribute): right})
        #print "Assigned:", self.left_attribute, right


class Task(object):
    """
    This class implements a task with one or more inputs and
    any number of outputs.
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
        assert parent is not None
        assert name   is not None
        self._parent     = parent
        self.id          = None
        self.name        = name
        self.inputs      = []
        self.outputs     = []
        self.pre_func    = None
        self.user_func   = None
        self.post_func   = None
        self.manual      = False
        self.internal    = False  # Only for easing debugging.
        self.cancelled   = False
        self.properties  = {}
        self.prop_assign = kwargs.get('property_assign', [])
        self.pre_assign  = kwargs.get('pre_assign',      [])
        self.post_assign = kwargs.get('post_assign',     [])
        self.locks       = kwargs.get('lock',            [])
        self._parent.add_notify(self)
        assert self.id is not None


    def set_attribute(self, **kwargs):
        """
        Defines the given attribute/value pairs.
        """
        self.properties.update(kwargs)


    def get_attribute(self, name, default = None):
        """
        Returns the value of the property with the given name, or the given
        default value if the property does not exist.

        name -- a property name (string)
        default -- the default value that is returned if the property does not
                   exist.
        """
        if self.properties.has_key(name):
            return self.properties[name]
        return default


    def connect(self, task):
        """
        Connect the *following* task to this one. In other words, the
        given task is added as an output task.

        task -- the task to connect to.
        """
        self.outputs.append(task)
        task.connect_notify(self)


    def connect_notify(self, task):
        """
        Called by the previous task to let us know that it exists.

        task -- the task by which this method is executed
        """
        self.inputs.append(task)


    def get_activated_branch_nodes(self, branch_node):
        """
        Returns the list of branch_nodes that were activated in the previous
        call of execute().

        branch_node -- the branch_node in which this method is executed
        """
        my_branch_node = branch_node.find_ancestor(self)
        return my_branch_node.children


    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        if self.id is None:
            raise WorkflowException(self, 'Task is not yet instanciated.')
        if len(self.inputs) < 1:
            raise WorkflowException(self, 'No input task connected.')


    def cancel(self, branch_node):
        """
        May be called by another task to cancel the operation before it was
        completed.
        If branch_node is None, all positions in the branch that use this
        task are cancelled. If branch_node is given, only the given branch is
        cancelled.
        """
        if branch_node.task == self:
            if branch_node.task != self:
                msg = 'Given branch points to %s!' % branch_node.name
                raise WorkflowException(self, msg)
            branch_node.cancel()
            for child in branch_node.children:
                child.task.cancel(child)
            return
        
        # Cancel my own branch nodes and those of the children.
        self.cancelled = True
        cancel         = []
        for node in branch_node.job.branch_tree:
            if node.thread_id != branch_node.thread_id:
                continue
            if node.task == self:
                cancel.append(node)
        for node in cancel:
            node.cancel()
            for child in node.children:
                child.task.cancel(child)


    def trigger(self, branch_node):
        """
        May be called by another task to trigger a task-specific
        event.
        """
        raise NotImplementedError("Trigger not supported for this task.")


    def predict(self, branch_node, seen = None):
        """
        Updates the branch such that all possible future routes are added
        with the PREDICTED flag.

        Should NOT be overwritten! Instead, overwrite the hook (_predict).
        """
        if seen is None:
            seen = []
        elif self in seen:
            return
        if branch_node.has_state(BranchNode.PREDICTED):
            seen.append(self)
        if not branch_node.has_state(BranchNode.COMPLETED) \
            and not branch_node.has_state(BranchNode.CANCELLED):
            self._predict(branch_node)
        for node in branch_node.children:
            node.task.predict(node, seen)


    def _predict(self, branch_node):
        branch_node.update_children(self.outputs, BranchNode.PREDICTED)


    def _ready_to_proceed(self, branch_node):
        return True


    def execute(self, branch_node):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.

        branch_node -- the branch_node in which this method is executed
        """
        assert branch_node is not None
        assert not self.cancelled
        self.test()

        # Acquire locks, if any.
        for lock in self.locks:
            mutex = branch_node.job.get_mutex(lock)
            if not mutex.testandset():
                return False

        result = False
        if self._ready_to_proceed(branch_node):
            # Assign variables, if so requested.
            for assignment in self.prop_assign:
                assignment.assign(branch_node.job, self)
            for assignment in self.pre_assign:
                assignment.assign(branch_node.job, branch_node.job)

            # Run user code, if any.
            if self.pre_func is not None:
                self.pre_func(branch_node, self)

            result = self._execute(branch_node)

            # Run user code, if any.
            if result and self.user_func is not None:
                result = self.user_func(branch_node, self)

            # Assign variables, if so requested.
            for assignment in self.post_assign:
                assignment.assign(branch_node.job, branch_node.job)

            # Run user code, if any.
            if self.post_func is not None:
                self.post_func(branch_node, self)

        # Release locks, if any.
        for lock in self.locks:
            mutex = branch_node.job.get_mutex(lock)
            mutex.unlock()

        if result:
            branch_node.set_state(BranchNode.COMPLETED)
        branch_node.job.task_completed_notify(self)

        return result


    def _execute(self, branch_node):
        """
        A hook into execute() that does the real work.

        branch_node -- the branch_node in which this method is executed
        """
        # If we have more than one output, implicitly split.
        branch_node.update_children(self.outputs)

        return True
