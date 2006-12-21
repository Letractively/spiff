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

class TaskIterator:
    def __init__(self, root_task, path = [0]):
        assert root_task is not None
        self.__initial_path = path
        self.__root_task    = root_task
        self.__current_path = self.__initial_path[:]


    def __iter__(self):
        self.__current_path = self.__initial_path[:]
        return self 


    def __get_task_from_path(self, path):
        task = self.__root_task
        for index in path:
            task = task.get(index)
            if not task:
                return None
        return task


    def current_path(self):
        return self.__current_path


    def current_depth(self):
        return len(self.__current_path)


    def next(self):
        if len(self.__current_path) == 0:
            raise StopIteration

        # Fetch the current task.
        task = self.__get_task_from_path(self.__current_path)
        if not task:
            raise StopIteration

        # If the current task has children, select the first one.
        last_task = task
        task = task.get(0)
        if task is not None:
            self.__current_path.append(0)
            return last_task
        
        # Otherwise, select the next item from the path.
        while len(self.__current_path) > 0:
            self.__current_path[-1] += 1
            task = self.__get_task_from_path(self.__current_path)
            if task is not None:
                break
            self.__current_path.pop()
        return last_task


    def reset(self):
        self.__current_path = []


if __name__ == '__main__':
    import unittest
    from TaskGroup   import TaskGroup
    from CommandTask import CommandTask

    class TaskIteratorTest(unittest.TestCase):
        def runTest(self):
            task2_2_2 = CommandTask('2.2.2', '', '')
            task2_2_1 = TaskGroup('2.2.1')
            task2_2   = TaskGroup('2.2', [task2_2_1, task2_2_2])
            task2_1   = TaskGroup('2.1')
            task3     = TaskGroup('3')
            task2     = TaskGroup('2', [task2_1, task2_2])
            task1     = TaskGroup('1')
            root_task = TaskGroup('root', [task1, task2, task3])
            iterator  = TaskIterator(root_task)
            count     = 0
            for task in iterator:
                count += 1
                #print "Name:", task.get_name()
            assert count == 7
            count     = 0
            for task in iterator:
                count += 1
                #print "Name:", task.get_name()
            assert count == 7

    testcase = TaskIteratorTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
