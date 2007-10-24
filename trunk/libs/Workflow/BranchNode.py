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

class BranchNode(object):
    """
    This class implements a node for composing a tree that represents the
    taken/not yet taken path within the workflow.
    """
    WAITING   =  1
    CANCELLED =  2
    COMPLETED =  4
    PREDICTED =  8
    TRIGGERED = 16

    class Iterator(object):
        """
        This is a tree iterator that supports filtering such that a client
        may walk through all nodes that have a specific state.
        """
        def __init__(self, current, filter = None):
            """
            Constructor.
            """
            self.filter = filter
            self.path   = [current]
        
        def __iter__(self):
            return self


        def next(self):
            # Make sure that the end is not yet reached.
            if len(self.path) == 0:
                raise StopIteration()

            # If the current node has children, the first child is the next item.
            # If the current node is PREDICTED, and predicted nodes are not
            # specificly searched, we can ignore the children, because predicted
            # nodes should only have predicted children.
            current     = self.path[-1]
            ignore_node = False
            if self.filter is not None:
                search_predicted = self.filter   & BranchNode.PREDICTED != 0
                is_predicted     = current.state & BranchNode.PREDICTED != 0
                ignore_node      = is_predicted and not search_predicted
            if len(current.children) > 0 and not ignore_node:
                self.path.append(current.children[0])
                if self.filter is not None and current.state & self.filter == 0:
                    return self.next()
                return current

            # Ending up here, this node has no children. Crop the path until we
            # reach a node that has unvisited children, or until we hit the end.
            while True:
                old_child = self.path.pop(-1)
                if len(self.path) == 0:
                    break

                # If this node has a sibling, choose it.
                parent = self.path[-1]
                pos    = parent.children.index(old_child)
                if len(parent.children) > pos + 1:
                    self.path.append(parent.children[pos + 1])
                    break
            if self.filter is not None and current.state & self.filter == 0:
                return self.next()
            return current


    # Pool for assigning a unique id to every new BranchNode.
    id_pool        = 0
    thread_id_pool = 0

    def __init__(self, job, task, parent = None):
        """
        Constructor.
        """
        assert job  is not None
        assert task is not None
        self.__class__.id_pool += 1
        self.job       = job
        self.parent    = parent
        self.children  = []
        self.state     = BranchNode.WAITING
        self.task      = task
        self.id        = self.__class__.id_pool
        self.thread_id = self.__class__.thread_id_pool
        self.name      = 'BranchNode for ' + self.task.name
        if parent is not None:
            self.parent._child_added_notify(self)


    def __iter__(self):
        return BranchNode.Iterator(self)


    def __setstate__(self, dict):
        self.__dict__.update(dict)
        # If unpickled in the same Python process in which a workflow
        # (BranchNode) is built through the API, we need to make sure
        # that there will not be any ID collisions.
        if dict['id'] >= self.__class__.id_pool:
            self.__class__.id_pool = dict['id']
        if dict['thread_id'] >= self.__class__.thread_id_pool:
            self.__class__.thread_id_pool = dict['thread_id']


    def _get_root(self):
        """
        Returns the first item in the branch.
        """
        if self.parent is None:
            return self
        return self.parent._get_root()


    def _child_added_notify(self, child):
        """
        Called by another BranchNode to let us know that a child was added.
        """
        assert child is not None
        self.children.append(child)


    def cancel(self):
        """
        Cancels the item if it was not yet completed, and removes
        any children that are PREDICTED.
        """
        if self.state & self.COMPLETED != 0:
            return
        self.state = self.CANCELLED | (self.state & self.TRIGGERED)
        self.drop_predicted_children()


    def drop_predicted_children(self):
        drop = []
        for child in self.children:
            if child.state & self.PREDICTED != 0:
                drop.append(child)
        for node in drop:
            self.children.remove(node)


    def set_state(self, state):
        """
        Called by the associated task to let us know that its state
        has changed (e.g. from WAITING to COMPLETED.)
        If recursive is True, the state is applied to the tree recursively.
        """
        self.state = state | (self.state & self.TRIGGERED)


    def has_state(self, state):
        """
        Returns True if the BranchNode has the given state flag set.
        """
        return (self.state & state) != 0


    def add_child(self, task, state = WAITING):
        """
        Adds a new child node and assigns the given task to the new node.

        task -- the task that is assigned to the new node.
        state -- the initial node state
        """
        if task is None:
            raise WorkflowException(self, 'add_child() requires a task.')
        if self.state & self.PREDICTED != 0 and state & self.PREDICTED == 0:
            msg = 'Attempt to add non-predicted child to predicted node'
            raise WorkflowException(self, msg)
        node = BranchNode(self.job, task, self)
        node.thread_id = self.thread_id
        node.state     = state
        return node


    def assign_new_thread_id(self, recursive = True):
        """
        Assigns a new thread id to the node.
        Returns the new id.
        """
        self.__class__.thread_id_pool += 1
        self.thread_id = self.__class__.thread_id_pool
        if not recursive:
            return self.thread_id
        for node in self:
            node.thread_id = self.thread_id
        return self.thread_id


    def update_children(self, tasks, state = WAITING):
        """
        This method adds one child for each given task, unless that
        child already exists.
        The state for newly added children, as well as the state for
        existing PREDICTED children is set to the given value.
        The state of existing non-PREDICTED children is left unchanged.

        If the node currently has a PREDICTED child that is not given in the
        tasks, the child is removed.
        It is an error if the node has a non-PREDICTED child that is not given
        in the tasks.

        Special case: Children with the state flag TRIGGERED set are ignored
        and never touched.

        task -- the list of tasks that may become children.
        state -- the state for newly added children
        """
        if tasks is None:
            raise WorkflowException(self, '"tasks" argument is None.')
        if type(tasks) != type([]):
            tasks = [tasks]

        # Create a list of all children that are no longer needed, and
        # set the state of all others.
        add    = tasks[:]
        remove = []
        for child in self.children:
            # Must not be TRIGGERED or COMPLETED.
            if child.state & BranchNode.TRIGGERED != 0:
                continue

            # Check whether the item needs to be added or removed.
            if child.task not in add:
                if child.state & BranchNode.PREDICTED == 0:
                    msg = 'Attempt to remove non-predicted %s' % child.name
                    raise WorkflowException(self, msg)
                remove.append(child)
                continue
            add.remove(child.task)

            # Update the state.
            if child.state & self.PREDICTED != 0:
                child.state = state

        # Remove all children that are no longer specified.
        for child in remove:
            self.children.remove(child)

        # Add a new child for each of the remaining tasks.
        for task in add:
            if task.cancelled:
                continue
            self.add_child(task, state)


    def is_descendant_of(self, parent):
        """
        Returns True if parent is in the list of ancestors, returns False
        otherwise.

        parent -- the parent that is searched in the ancestors.
        """
        if self.parent is None:
            return False
        if self.parent == parent:
            return True
        return self.parent.is_descendant_of(parent)


    def find_child_of(self, parent_task):
        """
        Returns the ancestor that has a BranchNode with the given Task
        as a parent.
        If no such ancestor was found, the root node is returned.

        parent_task -- the wanted parent Task
        """
        if self.parent is None:
            return self
        if self.parent.task == parent_task:
            return self
        return self.parent.find_child_of(parent_task)


    def find_any(self, task):
        """
        Returns any descendants that have the given task assigned.

        task -- the wanted task
        """
        instances = []
        if self.task == task:
            instances.append(self)
        for node in self:
            if node.task != task:
                continue
            instances.append(node)
        return instances


    def find_ancestor(self, task):
        """
        Returns the ancestor that has the given task assigned.
        If no such ancestor was found, the root node is returned.

        task -- the wanted task
        """
        if self.parent is None:
            return self
        if self.parent.task == task:
            return self.parent
        return self.parent.find_ancestor(task)


    def get_dump(self, indent = 0):
        """
        Returns the subtree as a string for debugging.
        """
        dbg  = (' ' * indent * 2)
        dbg += '%s/'           % self.id
        dbg += '%s:'           % self.thread_id
        dbg += ' %s'           % self.name
        dbg += ' State: %s'    % self.state
        dbg += ' Children: %s' % len(self.children)
        for child in self.children:
            dbg += '\n' + child.get_dump(indent + 1)
        return dbg


    def dump(self, indent = 0):
        """
        Prints the subtree as a string for debugging.
        """
        print self.get_dump()
