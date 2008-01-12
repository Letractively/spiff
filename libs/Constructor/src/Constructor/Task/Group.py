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

class Group(Task):
    def __init__(self, name = '', child_task = []):
        assert name       is not None
        assert child_task is not None
        Task.__init__(self, name)
        if type(child_task) == type([]):
            self._child_task = child_task
        else:
            self._child_task = [child_task]


    def append(self, task):
        assert task is not None
        self._child_task.append(task)


    def get(self, n):
        """
        Returns the child task at the given index.
        """
        assert n >= 0
        if n + 1 > len(self._child_task):
            return None
        return self._child_task[n]


    def install(self, environment):
        return Task.success


    def uninstall(self, environment):
        return Task.success


if __name__ == '__main__':
    import unittest
    import cgi
    from WebEnvironment import WebEnvironment
    from ExecCommand    import ExecCommand

    class GroupTest(unittest.TestCase):
        def runTest(self):
            environment = WebEnvironment(cgi.FieldStorage())
            task1       = ExecCommand('Subtask 1', 'True',  'True')
            task2       = ExecCommand('Subtask 2', 'False', 'False')
            gname       = 'Test Task Group'
            group       = Group(gname, [task1, task2])
            assert group.get_name()             == gname
            assert task1.install(environment)   == Task.success
            assert task2.install(environment)   == Task.failure
            assert task1.uninstall(environment) == Task.success
            assert task2.uninstall(environment) == Task.failure
            assert group.install(environment)   == Task.success
            assert group.uninstall(environment) == Task.success

    testcase = GroupTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
