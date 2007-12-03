# Copyright (C) 2006 Samuel Abels, http://debain.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
class Chunk(object):
    def __init__(self, type, data = '', name = ''):
        self.id          = -1
        self.type        = type
        self.data        = data
        self.name        = name
        self.children    = []
        self.child_types = {}
        self.child_names = {}


    def set_id(self, id):
        assert id is not None
        self.id = id


    def get_id(self):
        return self.id


    def get_type(self):
        """
        Returns the type of this chunk.
        """
        return self.type


    def get_data(self, recursive = True):
        """
        Returns the complete chunk (including all children, if recursive is
        True) in one string.
        
        @rtype:  string
        @return: The contents of the file.
        """
        if not recursive:
            return self.data
        complete = self.data
        #print "%s START: '%s'" % (self.get_type(), complete)
        for child in self.children:
            complete += child.get_data()
        #print "%s END: '%s'" % (self.get_type(), complete)
        return complete


    def get_name(self):
        """
        Returns the name of this chunk.
        """
        return self.name


    def add_child(self, child):
        """
        Adds another chunk below this chunk.
        
        @type  child: Chunk
        @param child: The chunk to be inserted.
        @rtype:  Chunk
        @return: The given chunk.
        """
        assert child is not None
        self.children.append(child)
        if not self.child_types.has_key(child.get_type()):
            self.child_types[child.get_type()] = [child]
            self.child_names[child.get_type()] = {child.get_name(): child}
        else:
            self.child_types[child.get_type()].append(child)
            self.child_names[child.get_type()][child.get_name()] = child
        return child


    def get_child(self, type, name = ''):
        """
        Returns the first child with the given type and name.
        
        @type  type: string
        @param type: The type of the child that this function returns.
        @type  name: string
        @param name: The name of the child that this function returns.
        @rtype:  Chunk
        @return: The requested chunk, or None.
        """
        assert type is not None
        assert name is not None
        if not self.child_names.has_key(type):
            return None
        if not self.child_names[type].has_key(name):
            return None
        return self.child_names[type][name]


    def get_child_list(self, type = None):
        """
        Returns a list of all chunks that are direct children of this chunk.
        If a type is given, only chunks with the given types are returned.
        
        @type  type: string
        @param type: The type of the children that this function returns.
        @rtype:  list
        @return: The list of children with the requested type.
        """
        if type is not None:
            return self.child_types[type]
        else:
            return self.children


    def get_n_children(self, type = None):
        """
        Returns the number of children with the given type.
        
        @type  type: string
        @param type: The type of the children that this function returns.
        @rtype:  int
        @return: The number of children with the requested type.
        """
        if type is None:
            return len(self.children)
        if self.child_types.has_key(type):
            return len(self.child_types[type])
        return 0
