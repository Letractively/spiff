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

class TaskIterator:
    def __init__(self, root_task, path = []):
        assert root_task is not None
        self.__current_path = path
        self.__root_task    = root_task


    def __iter__(self):
        return self 


    def __get_task_from_path(self, path):
        task = self.__root_task
        for index in self.path:
            task = task.get(index)
            if not task:
                return None
        return task


    def next(self):
        # Fetch the current task.
        task = self.__get_task_from_path(self, self.__current_path)
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
            task = self.__get_task_from_path(self, self.__current_path)
            if task is not None:
                break
            self.__current_path.pop()
        return last_task


    def reset(self):
        self.__current_path = []
