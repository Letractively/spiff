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
from Guard import Action

class CreateAction(Task):
    def __init__(self, action_name, action_handle, section_handle):
        Task.__init__(self, 'Creating action \'%s\'' % action_name)
        self.__action_name    = action_name
        self.__action_handle  = action_handle
        self.__section_handle = section_handle


    def install(self, environment):
        key     = 'action_section_' + self.__section_handle
        section = environment.get_attribute(key)
        guard   = environment.get_attribute('guard_db')
        assert guard is not None
        assert section is not None
        try:
            handle = self.__action_handle
            action = guard.get_action_from_handle(handle,
                                                  self.__section_handle)
            if not action:
                action = Action(self.__action_name, handle)
                guard.add_action(action, section)
        except:
            return Task.failure
        environment.set_attribute('action_' + handle, action)
        return Task.success


    def uninstall(self, environment):
        return Task.success


if __name__ == '__main__':
    import unittest
    import cgi
    from ConfigParser import RawConfigParser
    from WebEnvironment import WebEnvironment

    class CreateActionTest(unittest.TestCase):
        def runTest(self):
            environment = WebEnvironment(cgi.FieldStorage())
            task        = CreateAction()
            #FIXME:assert task.install(environment)   == Task.success
            assert task.uninstall(environment) == Task.success

    testcase = CreateActionTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
