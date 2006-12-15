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
        Task.__init__(self, name, '')
        if type(child_task) == type([]):
            self.__child_task = child_task
        else:
            self.__child_task = [child_task]


    def execute(self):
        for task in self.__child_task:
            if not task.execute():
                return False
        return True


if __name__ == '__main__':
    import unittest

    class TaskGroupTest(unittest.TestCase):
        def runTest(self):
            task1 = Task('Subtask 1', 'True')
            task2 = Task('Subtask 2', 'False')
            gname = 'Test Task Group'
            group = TaskGroup(gname, [task1, task2])
            assert group.get_name() == gname
            assert task1.execute()  == True
            assert task2.execute()  == False
            assert group.execute()  == False

    testcase = TaskGroupTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
