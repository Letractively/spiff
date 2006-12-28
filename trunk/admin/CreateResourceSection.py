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
from Task import Task
from Guard import ResourceSection

class CreateResourceSection(Task):
    def __init__(self, section_name, section_handle):
        Task.__init__(self, 'Creating resource section \'%s\'' % section_name)
        self.__section_name   = section_name
        self.__section_handle = section_handle


    def install(self, environment):
        guard = environment.get_attribute('guard_db')
        assert guard is not None
        try:
            handle  = self.__section_handle
            section = guard.get_resource_section_from_handle(handle)
            if section is None:
                section = ResourceSection(self.__section_name, handle)
                guard.add_resource_section(section)
        except:
            return Task.failure
        environment.set_attribute('resource_section_' + self.__section_handle,
                                  section)
        return Task.success


    def uninstall(self, environment):
        return Task.success


if __name__ == '__main__':
    import unittest
    import cgi
    from ConfigParser import RawConfigParser
    from WebEnvironment import WebEnvironment

    class CreateResourceSectionTest(unittest.TestCase):
        def runTest(self):
            environment = WebEnvironment(cgi.FieldStorage())
            task        = CreateResourceSection()
            #FIXME:assert task.install(environment)   == Task.success
            assert task.uninstall(environment) == Task.success

    testcase = CreateResourceSectionTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
