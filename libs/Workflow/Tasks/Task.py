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
from AbstractMethod import AbstractMethod
from BranchNode     import *
from Exception      import WorkflowException

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
        """
        assert parent is not None
        assert name   is not None
        self._parent   = parent
        self.id        = None
        self.name      = name
        self.inputs    = []
        self.outputs   = []
        self.pre_func  = None
        self.user_func = None
        self.post_func = None
        self.manual    = False
        self.internal  = False  # Only for easing debugging.
        self.locks     = kwargs.get('lock', [])
        self._parent.add_notify(self)
        assert self.id is not None


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


    def get_activated_branch_nodes(self, job, branch_node):
        """
        Returns the list of branch_nodes that were activated in the previous call
        of execute().

        job -- the job in which this method is executed
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


    def trigger(self, job, branch_node):
        """
        May be called by another task to trigger a task-specific
        event.
        """
        AbstractMethod()


    def predict(self, job, branch_node, seen = None):
        """
        Updates the branch such that all possible future routes are added
        with the PREDICTED flag.

        Should NOT be overwritten! Instead, overwrite the hook (_predict).
        """
        if seen is None:
            seen = []
        elif self in seen:
            return
        if branch_node.state & BranchNode.PREDICTED != 0:
            seen.append(self)
        if branch_node.state & BranchNode.COMPLETED == 0 \
            and branch_node.state & BranchNode.CANCELLED == 0:
            self._predict(job, branch_node)
        for node in branch_node.children:
            node.task.predict(job, node, seen)


    def _predict(self, job, branch_node):
        branch_node.update_children(self.outputs, BranchNode.PREDICTED)


    def execute(self, job, branch_node):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.

        job -- the job in which this method is executed
        branch_node -- the branch_node in which this method is executed
        """
        assert job         is not None
        assert branch_node is not None
        self.test()

        # Acquire locks, if any.
        for lock in self.locks:
            mutex = job.get_mutex(lock)
            if not mutex.testandset():
                return False

        # Run user code, if any.
        if self.pre_func is not None:
            self.pre_func(job, branch_node, self)

        result = self._execute(job, branch_node)

        # Run user code, if any.
        if result and self.user_func is not None:
            result = self.user_func(job, branch_node, self)
        if self.post_func is not None:
            self.post_func(job, branch_node, self)

        # Release locks, if any.
        for lock in self.locks:
            mutex = job.get_mutex(lock)
            mutex.unlock()

        if result:
            branch_node.set_status(BranchNode.COMPLETED)

        return result


    def _execute(self, job, branch_node):
        """
        A hook into execute() that does the real work.

        job -- the job in which this method is executed
        branch_node -- the branch_node in which this method is executed
        """
        # If we have more than one output, implicitly split.
        branch_node.update_children(self.outputs)
        return True