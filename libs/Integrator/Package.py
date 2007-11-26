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
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Guard     import Resource
from functions import descriptor_parse

class Package(Resource):
    def __init__(self, name, handle = None, version = '0'):
        assert name    is not None
        assert version is not None
        Resource.__init__(self, name, handle)
        self.set_version(version)
        self.__dependencies = {}


    def set_author(self, author):
        assert author is not None and author != ''
        self.set_attribute('author', author)


    def get_author(self):
        return self.get_attribute('author')


    def set_description(self, description):
        assert description is not None
        self.set_attribute('description', description)


    def get_description(self):
        return self.get_attribute('description')


    def set_version(self, version):
        assert version is not None and version != ''
        self.set_attribute('version', version)


    def get_version(self):
        return self.get_attribute('version')


    def set_filename(self, filename):
        assert filename is not None
        self.set_attribute('filename', filename)


    def get_filename(self):
        return self.get_attribute('filename')


    def add_dependency(self, descriptor, context = 'default'):
        assert descriptor is not None and descriptor is not ''
        assert context    is not None and context    is not ''
        #print "Descriptor:", descriptor
        matches = descriptor_parse(descriptor)
        assert matches is not None
        if not self.__dependencies.has_key(context):
            self.__dependencies[context] = [descriptor]
        else:
            self.__dependencies[context].append(descriptor)


    def get_dependency_context_list(self):
        return self.__dependencies.keys()


    def get_dependency_list(self, context = None):
        if context is not None:
            return self.__dependencies[context]
        dependency_list = []
        for context in self.__dependencies:
            dependency_list += self.__dependencies[context]
        return dependency_list
