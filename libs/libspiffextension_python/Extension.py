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
sys.path.append('..')
from functions          import descriptor_parse
from libspiffacl_python import Resource

class Extension(Resource):
    def __init__(self, name, handle = None, version = '0'):
        assert name    is not None
        assert version is not None
        Resource.__init__(self, name, handle)
        self.set_version(version)
        self.__dependencies = {}


    def set_version(self, version):
        assert version is not None and version != ''
        self.set_attribute('version', version)


    def get_version(self):
        return self.get_attribute('version')


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


    def set_filename(self, filename):
        assert filename is not None
        self.set_attribute('filename', filename)


    def get_filename(self):
        return self.get_attribute('filename')


    def add_dependency(self, descriptor, context = 'default'):
        assert descriptor is not None and descriptor is not ''
        assert context    is not None and context    is not ''
        matches = descriptor_parse(descriptor)
        assert matches is not None
        if not self.__dependencies.has_key(context):
            self.__dependencies[context] = [descriptor]
        else:
            self.__dependencies[context].append(descriptor)


    def get_dependency_context_list(self):
        return self.__dependencies.keys()


    def get_dependency_list(self, context):
        return self.__dependencies[context]


if __name__ == '__main__':
    import unittest

    class ExtensionTest(unittest.TestCase):
        def runTest(self):
            name      = 'Test Extension'
            handle    = 'Test Handle'
            version   = '0.1.2'
            author    = 'Test Author'
            descr     = 'let me test this'
            filename  = '/my/filename.tgz'
            context   = 'Test Context'
            extension = Extension(name, handle, version)
            assert extension.get_name()    == name
            assert extension.get_handle()  == handle
            assert extension.get_version() == version

            extension = Extension(name)
            assert extension.get_name()    == name
            assert extension.get_handle()  == 'test_extension'
            assert extension.get_version() == '0'

            extension.set_version(version)
            extension.set_author(author)
            extension.set_description(descr)
            extension.set_filename(filename)
            assert extension.get_version()     == version
            assert extension.get_author()      == author
            assert extension.get_description() == descr
            assert extension.get_filename()    == filename

            # Test empty context list.
            context_list = extension.get_dependency_context_list()
            assert len(context_list) == 0

            # Test non-empty context list.
            descriptor = 'spiff>=1.0'
            extension.add_dependency(descriptor)
            context_list = extension.get_dependency_context_list()
            assert context_list[0] == 'default'
            assert len(context_list) == 1

            # Test dependency list.
            dep_list = extension.get_dependency_list('default')
            assert dep_list[0] == descriptor
            assert len(dep_list) == 1

            # Test non-default context.
            context     = 'runtime'
            descriptor1 = 'mydep=0.1.2'
            descriptor2 = 'mydep2>=2'
            extension.add_dependency(descriptor1, context)
            extension.add_dependency(descriptor2, context)
            context_list = extension.get_dependency_context_list()
            assert context_list[0] == 'default'
            assert context_list[1] == context
            assert len(context_list) == 2

            dep_list = extension.get_dependency_list('default')
            assert dep_list[0] == descriptor
            assert len(dep_list) == 1
            dep_list = extension.get_dependency_list(context)
            assert dep_list[0] == descriptor1
            assert dep_list[1] == descriptor2
            assert len(dep_list) == 2
            
    testcase = ExtensionTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
