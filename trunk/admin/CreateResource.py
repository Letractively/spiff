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
from Task  import Task
from Guard import Resource

class CreateResource(Task):
    def __init__(self,
                 resource_name,
                 resource_handle,
                 section_handle,
                 parent_handle = None):
        Task.__init__(self, 'Creating resource \'%s\'' % resource_name)
        self.__resource_name   = resource_name
        self.__resource_handle = resource_handle
        self.__section_handle  = section_handle
        self.__parent_handle   = parent_handle


    def install(self, environment):
        key     = 'resource_section_' + self.__section_handle
        section = environment.get_attribute(key)
        guard   = environment.get_attribute('guard_db')
        parent  = None
        if self.__parent_handle is not None:
            key    = 'resource_' + self.__parent_handle
            parent = environment.get_attribute(key)
        assert guard   is not None
        assert section is not None
        try:
            handle = self.__resource_handle
            resource = guard.get_resource_from_handle(handle,
                                                      self.__section_handle)
            if not resource:
                parent_id = None
                if parent:
                    parent_id = parent.get_id()
                resource = Resource(self.__resource_name, handle)
                guard.add_resource(parent_id, resource, section)
        except:
            return Task.failed
        environment.set_attribute('resource_' + handle, resource)
        return Task.success


    def uninstall(self, environment):
        return Task.success


if __name__ == '__main__':
    import unittest
    import cgi
    from ConfigParser import RawConfigParser
    from WebEnvironment import WebEnvironment

    class CreateResourceTest(unittest.TestCase):
        def runTest(self):
            environment = WebEnvironment(cgi.FieldStorage())
            task        = CreateResource()
            #FIXME:assert task.install(environment)   == Task.success
            assert task.uninstall(environment) == Task.success

    testcase = CreateResourceTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
