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

class CommandTask(Task):
    def __init__(self, name, install_cmd, uninstall_cmd):
        assert name          is not None
        assert install_cmd   is not None
        assert uninstall_cmd is not None
        Task.__init__(self, name)
        self.__install_cmd   = install_cmd
        self.__uninstall_cmd = uninstall_cmd


    def __do_command(self, environment, cmd):
        ret = eval(cmd)
        if ret:
            result = self.success
            hint   = ''
        else:
            result = self.failure
            hint   = '"' + cmd + '" failed'
        environment.task_done(self._name, self._result_msg[result], hint)
        return result


    def install(self, environment):
        return self.__do_command(environment, self.__install_cmd)


    def uninstall(self, environment):
        return self.__do_command(environment, self.__uninstall_cmd)


if __name__ == '__main__':
    import unittest
    import cgi
    from WebEnvironment import WebEnvironment

    class CommandTaskTest(unittest.TestCase):
        def runTest(self):
            environment = WebEnvironment(cgi.FieldStorage())
            name1       = 'Task 1'
            name2       = 'Task 2'
            task1       = CommandTask(name1,
                                      'True  #install',
                                      'False #uninstall')
            task2       = CommandTask(name2,
                                      'False #install',
                                      'True  #uninstall')
            assert task1.get_name()             == name1
            assert task2.get_name()             == name2
            assert task1.install(environment)   == Task.success
            assert task2.install(environment)   == Task.failure
            assert task1.uninstall(environment) == Task.failure
            assert task2.uninstall(environment) == Task.success

    testcase = CommandTaskTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
