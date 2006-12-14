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
class Variable:
    def __init__(self, name, type = None):
        self.id   = -1
        self.name = name
        self.type = type
        self.docs = ''


    def set_id(self, id):
        assert id is not None
        self.id = id


    def get_id(self):
        return self.id


    def get_name(self):
        return self.name


    def set_type(self, type):
        self.type = type


    def get_type(self):
        return self.type


    def set_docs(self, docs):
        self.docs = docs


    def get_docs(self):
        return self.docs
