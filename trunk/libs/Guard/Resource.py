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
from DBObject import *

class Resource(DBObject):
    def __init__(self, name, handle = None):
        DBObject.__init__(self, name, handle)
        self._n_children     = 0
        self._attribute_list = {}

    def is_group(self):
        return False

    def set_n_children(self, n_children):
        self._n_children = int(n_children)

    def get_n_children(self):
        return self._n_children

    def set_attribute(self, name, value):
        self._attribute_list[name] = value

    def get_attribute(self, name):
        return self._attribute_list.get(name, None)

    def remove_attribute(self, name):
        if self._attribute_list.has_key(name):
            del self._attribute_list[name]

    def set_attribute_list(self, list):
        self._attribute_list = list

    def get_attribute_list(self):
        return self._attribute_list
