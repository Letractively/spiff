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
from Branch import Branch

class Job(object):
    """
    This class implements the engine that executes a workflow.
    It is a essentially a facility for managing all branches.
    A Job is also the place that holds the attributes of a running workflow.
    """

    def __init__(self, workflow):
        """
        Constructor.
        """
        assert workflow is not None
        self.workflow      = workflow
        self.attributes    = {}
        self.context_data  = {}
        self.branch_list   = {}
        self.id_pool       = 1
        self.branch_list['1'] = Branch(self.id_pool, self, workflow.start)


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


    def branch_completed_notify(self, branch):
        """
        Called by an associated branch when it has completed.

        branch -- the branch that has completed. (Branch)
        """
        assert self.branch_list['%s' % branch.id] is not None
        del self.branch_list['%s' % branch.id]


    def split_branch(self, branch):
        """
        Splits the given Branch and adds the new branch to the same
        job. Returns the new Branch.

        branch -- the branch that has completed. (Branch)
        """
        self.id_pool += 1
        new_branch = branch.copy(self.id_pool)
        new_branch.clear_queue()
        self.branch_list['%s' % self.id_pool] = new_branch
        return new_branch


    def execute_all(self):
        """
        Runs all branches until completion.
        """
        while len(self.branch_list) > 0:
            branch_list = self.branch_list.copy()
            branch_ids  = [int(id) for id in branch_list.keys()]
            branch_ids.sort()
            for id in branch_ids:
                branch = branch_list['%s' % id]
                branch.execute_next()
