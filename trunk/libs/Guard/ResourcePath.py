# Copyright (C) 2007 Samuel Abels, http://debain.org
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
from string    import split
from functions import *

class ResourcePath(object):
    def __init__(self, path = ''):
        """
        Create a new instance.

        @type  path string or array
        @param path Contains the path in the following format: 0/1/2/...,
                    or as an array.
        """
        self.path = None
        self.set(path)


    def set(self, path = ''):
        """
        Point the object to the given path.

        @type  path string or array
        @param path Contains the path in the following format: 0/1/2/...,
                    or as an array.
        """
        self.path = []
        if len(path) == 0:
            return
        if type('') == type(path):
            path = [int(id) for id in split(path, '/')]
        for item in path:
            self.path.append(int(item))


    def get(self):
        """
        Returns the current path.
        """
        return '/'.join([str(id) for id in self.path])


    def hex(self):
        return list2hex_path(self.path)


    def bin(self):
        return list2bin_path(self.path)


    def __add__(self, other):
        return ResourcePath(self.path + other.path)


    def __len__(self):
        return len(self.path)


    def get_parent_id(self):
        """
        Returns the second-last element of the path.
        """
        if len(self.path) <= 1:
            return None
        return self.path[-2]


    def get_current_id(self):
        """
        Returns the last element of the path.
        """
        if len(self.path) == 0:
            return None
        return self.path[-1]


    def crop(self, n = 1):
        """
        Crops the path by n components and returns a ResourcePath that
        points to the new path.
        """
        if len(self.path) - n <= 0:
            return ResourcePath()
        return ResourcePath(self.path[:n * -1])


    def append(self, id):
        """
        Appends the given id to the path and returns a ResourcePath that
        points to the new path.
        """
        assert id is not None
        assert int(id) >= 0
        path = self.path[:]
        path.append(int(id))
        return ResourcePath(path)
