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
from functions import make_handle_from_string

class DBObject:
    def __init__(self, name, handle = None):
        self.__id     = -1
        self.__name   = name
        if handle == None:
            self.__handle = make_handle_from_string(name)
        else:
            self.__handle = handle

    def set_id(self, id):
        self.__id = int(id)

    def get_id(self):
        return self.__id

    def set_name(self, name):
        assert name != None
        assert len(name) > 0
        self.__name = name
        if len(self.__handle) == 0:
            self.__handle = make_handle_from_string(name)

    def get_name(self):
        return self.__name

    def set_handle(self, handle):
        self.__handle = handle

    def get_handle(self):
        return self.__handle

    __id     = property(set_id)
    __name   = property(set_name)
    __handle = property(set_handle)
