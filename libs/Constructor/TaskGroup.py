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

class TaskGroup(Task):
    def __init__(self, name = '', child_task = []):
        assert name       is not None
        assert child_task is not None
        Task.__init__(self, name)
        if type(child_task) == type([]):
            self.__child_task = child_task
        else:
            self.__child_task = [child_task]


    def append(self, task):
        assert task is not None
        self.__child_task.append(task)


    def get(self, n):
        """
        Returns the child task at the given index.
        """
        if n + 1 > len(self.__child_task):
            return None
        return self.__child_task[n]


    def install(self, renderer):
        if self._name != '':
            renderer.section_start(self._name)
        result = Task.success
        for task in self.__child_task:
            result = task.install(renderer)
            if result is not Task.success:
                break
        if self._name != '':
            renderer.section_end()
        return result


    def uninstall(self, renderer):
        if self._name != '':
            renderer.section_start(self._name)
        result = Task.success
        for task in self.__child_task:
            result = task.uninstall(renderer)
            if result is not Task.success:
                break
        if self._name != '':
            renderer.section_end()
        return result


if __name__ == '__main__':
    import unittest
    from WebRenderer import WebRenderer
    from CommandTask import CommandTask

    class TaskGroupTest(unittest.TestCase):
        def runTest(self):
            renderer = WebRenderer()
            task1    = CommandTask('Subtask 1', 'True',  'True')
            task2    = CommandTask('Subtask 2', 'False', 'False')
            gname    = 'Test Task Group'
            group    = TaskGroup(gname, [task1, task2])
            assert group.get_name()          == gname
            assert task1.install(renderer)   == Task.success
            assert task2.install(renderer)   == Task.failure
            assert task1.uninstall(renderer) == Task.success
            assert task2.uninstall(renderer) == Task.failure
            assert group.install(renderer)   == Task.failure
            assert group.uninstall(renderer) == Task.failure

    testcase = TaskGroupTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
