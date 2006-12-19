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
    def __init__(self, name, child_task):
        assert name       is not None
        assert child_task is not None
        Task.__init__(self, name)
        if type(child_task) == type([]):
            self.__child_task = child_task
        else:
            self.__child_task = [child_task]


    def install(self, renderer):
        renderer.section_start(self._name)
        for task in self.__child_task:
            if not task.install(renderer):
                renderer.section_end()
                return False
        renderer.section_end()
        return True


    def uninstall(self, renderer):
        renderer.section_start(self._name)
        for task in self.__child_task:
            if not task.uninstall(renderer):
                renderer.section_end()
                return False
        renderer.section_end()
        return True


if __name__ == '__main__':
    import unittest
    from CliRenderer import CliRenderer
    from WebRenderer import WebRenderer
    from CommandTask import CommandTask

    class TaskGroupTest(unittest.TestCase):
        def runTest(self):
            renderer = CliRenderer()
            renderer = WebRenderer()
            task1    = CommandTask('Subtask 1', 'True',  'True')
            task2    = CommandTask('Subtask 2', 'False', 'False')
            gname    = 'Test Task Group'
            group    = TaskGroup(gname, [task1, task2])
            assert group.get_name()          == gname
            assert task1.install(renderer)   == True
            assert task2.install(renderer)   == False
            assert task1.uninstall(renderer) == True
            assert task2.uninstall(renderer) == False
            assert group.install(renderer)   == False
            assert group.uninstall(renderer) == False

    testcase = TaskGroupTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
