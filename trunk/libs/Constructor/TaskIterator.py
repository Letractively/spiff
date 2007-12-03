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

class TaskIterator(object):
    def __init__(self, root_task, path = [0]):
        assert root_task is not None
        self.__initial_path = path
        self.__root_task    = root_task
        self.__next_path    = self.__initial_path[:]
        self.__current_path = self.__initial_path[:]


    def __iter__(self):
        self.__next_path    = self.__initial_path[:]
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
        # Fetch the task.
        self.__current_path = self.__next_path[:]
        current_task = self.__get_task_from_path(self.__current_path)
        if len(self.__current_path) == 0:
            raise StopIteration

        # If the current task has children, select the first one.
        next_task = current_task.get(0)
        if next_task is not None:
            self.__next_path.append(0)
            return current_task
        
        # Otherwise, select the next item from the path.
        while len(self.__next_path) > 0:
            self.__next_path[-1] += 1
            next_task = self.__get_task_from_path(self.__next_path)
            if next_task is not None:
                break
            self.__next_path.pop()
        return current_task


    def reset(self):
        self.__current_path = []
        self.__next_path    = []


if __name__ == '__main__':
    import unittest
    from Task import *

    class TaskIteratorTest(unittest.TestCase):
        def runTest(self):
            task2_2_2 = ExecCommand('2.2.2', '', '')
            task2_2_1 = Group('2.2.1')
            task2_2   = Group('2.2', [task2_2_1, task2_2_2])
            task2_1   = Group('2.1')
            task3     = Group('3')
            task2     = Group('2', [task2_1, task2_2])
            task1     = Group('1')
            root_task = Group('root', [task1, task2, task3])
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
