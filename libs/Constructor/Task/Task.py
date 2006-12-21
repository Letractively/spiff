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
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from TaskIterator import TaskIterator

class Task:
    success, failure, interact = range(3)
    _result_msg = {
      success: 'Success',
      failure: 'Failed',
      interact: 'Ineraction required'
    }
    
    def __init__(self, name):
        assert name is not None
        self._name = name


    def get_name(self):
        return self._name


    def get(self, n):
        return None


    def get_child_iter(self):
        return TaskIterator(self)


    def install(self, environment):
        assert False  # Must be implemented!


    def uninstall(self, environment):
        assert False  # Must be implemented!


if __name__ == '__main__':
    import unittest

    class TaskTest(unittest.TestCase):
        def runTest(self):
            name = 'Task 1'
            task = Task(name)
            assert task.get_name() == name


    testcase = TaskTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
