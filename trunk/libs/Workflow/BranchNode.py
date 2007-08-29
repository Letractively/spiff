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
        may walk through all nodes that have a specific status.
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
    id_pool = 0

    def __init__(self, job, activity, parent = None):
        """
        Constructor.
        """
        assert job      is not None
        assert activity is not None
        self.__class__.id_pool += 1
        self.job      = job
        self.parent   = parent
        self.children = []
        self.state    = BranchNode.WAITING
        self.activity = activity
        self.id       = self.__class__.id_pool
        self.name     = 'BranchNode for ' + self.activity.name
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
        Cancels all items in this branch. The status of any items that are
        already completed is not changed.
        """
        if self.state & BranchNode.COMPLETED == 0:
            self.state = BranchNode.CANCELLED
        for child in self.children:
            child.cancel()


    def set_status(self, status, recursive = False):
        """
        Called by the associated activity to let us know that its status
        has changed (e.g. from WAITING to COMPLETED.)
        If recursive is True, the status is applied to the tree recursively.
        """
        self.state = status
        if recursive == True:
            for child in self.children:
                child.set_status(status)


    def get_copy(self):
        """
        Creates a copy of this subtree, and returns a reference to the new
        node.
        """
        new_node = BranchNode(self.job, self.activity)
        for child in self.children:
            new_child = child.get_copy()
            new_child.parent = new_node
            new_node._child_added_notify(new_child)
        return new_node


    def split(self):
        """
        Like get_copy(), but also makes the new node a sibling of the current
        node. It is not possible to split the root node.
        """
        if self.parent is None:
            raise WorkflowException(self, 'Attempt to split the root node.')
        new_node = self.get_copy()
        new_node.parent = self.parent
        self.parent._child_added_notify(new_node)
        return new_node


    def add_child(self, activity, status = WAITING):
        """
        Adds a new child node and assigns the given activity to the new node.

        activity -- the activity that is assigned to the new node.
        status -- the initial node state
        """
        if activity is None:
            raise WorkflowException(self, 'add_child() requires an activity.')
        if self.state & self.PREDICTED != 0 and status & self.PREDICTED == 0:
            msg = 'Attempt to add non-predicted child to predicted node'
            raise WorkflowException(self, msg)
        node = BranchNode(self.job, activity, self)
        node.state = status
        return node


    def update_children(self, activities, status = WAITING):
        """
        This method adds one child for each given activity, unless that
        child already exists.
        The status for newly added children, as well as the state for
        existing PREDICTED children is set to the given value.
        The state of existing non-PREDICTED children is left unchanged.

        If the node currently has a PREDICTED child that is not given in the
        activities, the child is removed.
        It is an error if the node has a non-PREDICTED child that is not given
        in the activities.

        Special case: Children with the state flag TRIGGERED set are ignored
        and never touched.

        activity -- the list of activities that may become children.
        status -- the status for newly added children
        """
        if activities is None:
            raise WorkflowException(self, '"activities" argument is None.')
        if type(activities) != type([]):
            activities = [activities]

        # Create a list of all children that are no longer needed, and
        # set the status of all others.
        add    = activities[:]
        remove = []
        for child in self.children:
            if child.state & BranchNode.TRIGGERED != 0:
                continue
            if child.activity not in add:
                if child.state & BranchNode.PREDICTED != 0:
                    remove.append(child)
                else:
                    msg = '"activities" does not contain %s' % child.name
                    raise WorkflowException(self, msg)
                continue
            child.state = status
            add.remove(child.activity)

        # Remove all children that are no longer specified.
        for child in remove:
            self.children.remove(child)

        # Add a new child for each of the remaining activities.
        for activity in add:
            self.add_child(activity, status)


    def drop_children(self):
        """
        Removes all future activities (i.e. the children of this node) from
        the tree.
        """
        self.children = []


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


    def get_branch_start(self):
        """
        Returns the first activity from the position in the path after a
        split happened. In other words, returns the first ancestor that
        has at least one sibling.
        If no such parent was found, the root node is returned.
        """
        if self.parent is None:
            return self
        if len(self.parent.children) > 1:
            return self
        return self.parent.get_branch_start()


    def get_last_split(self):
        """
        Returns the last activity from the path at which a
        split happened. In other words, returns the first ancestor that
        has more than one child.
        If no such parent was found, the root node is returned.
        """
        if self.parent is None:
            return self
        if len(self.parent.children) > 1:
            return self.parent
        return self.parent.get_last_split()


    def get_child_of(self, parent):
        """
        Returns the ancestor that has the given BranchNode as a parent.
        If no such ancestor was found, the root node is returned.

        parent -- the wanted parent BranchNode
        """
        if self.parent is None:
            return self
        if self.parent == parent:
            return self
        return self.parent.get_child_of(parent)


    def find_ancestor(self, activity):
        """
        Returns the ancestor that has the given activity assigned.
        If no such ancestor was found, the root node is returned.

        activity -- the wanted activity
        """
        if self.parent is None:
            return self
        if self.parent.activity == activity:
            return self.parent
        return self.parent.find_ancestor(activity)


    def find_path(self, start = None, end = None):
        """
        Returns a copy of the path, beginning from the first occurence
        of the given start activity, and ending at the LAST occurence
        of the given end activity.

        start -- the activity at which the path begins. If None is given,
                 the path starts at the first activity.
        end -- the activity at which the path ends. If None is given,
               the complete path is returned.
        """
        path      = []
        current   = self
        start_pos = -1
        while current is not None:
            if len(path) == 0 \
                and end is not None \
                and current.activity is not end:
                current = current.parent
                continue
            path.append(current)
            if current == start:
                start_pos = current
            current = current.parent
        path = path[:start_pos]
        path.reverse()
        return '/'.join(['%s' % node.id for node in path])


    def get_dump(self, indent = 0):
        """
        Returns the subtree as a string for debugging.
        """
        dbg  = (' ' * indent * 2)
        dbg += '%s: ' % self.id
        dbg += '%s/'  % self.state
        dbg += '%s/'  % len(self.children)
        dbg += '%s'   % self.name
        for child in self.children:
            dbg += '\n' + child.get_dump(indent + 1)
        return dbg


    def dump(self, indent = 0):
        """
        Prints the subtree as a string for debugging.
        """
        print self.get_dump()