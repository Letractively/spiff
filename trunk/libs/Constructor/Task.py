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

class Task:
    __success, __failure = range(2)
    __result_msg = {__success: 'Success', __failure: 'Failed'}
    
    def __init__(self, name, command):
        assert name    is not None
        assert command is not None
        self._name     = name
        self.__command = command


    def get_name(self):
        return self._name


    def execute(self, renderer):
        ret = eval(self.__command)
        if ret:
            result = self.__success
            hint   = ''
        else:
            result = self.__failure
            hint   = '"' + self.__command + '" failed'
        renderer.task_done(self._name, self.__result_msg[result], hint)
        return ret


if __name__ == '__main__':
    import unittest
    from CliRenderer import CliRenderer

    class TaskTest(unittest.TestCase):
        def runTest(self):
            renderer = CliRenderer()
            name1    = 'Task 1'
            name2    = 'Task 2'
            task1    = Task(name1, 'True')
            task2    = Task(name2, 'False')
            assert task1.get_name()        == name1
            assert task2.get_name()        == name2
            assert task1.execute(renderer) == True
            assert task2.execute(renderer) == False


    testcase = TaskTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
