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
from Task         import Task
from TaskGroup    import TaskGroup
from TaskIterator import TaskIterator

class Constructor:
    def __init__(self, environment):
        assert environment is not None
        initial_path         = environment.get_task_path()
        self.__root_task     = TaskGroup()
        self.__task_iter     = TaskIterator(self.__root_task, initial_path)
        self.__environment   = environment


    def set_app_name(self, app_name):
        assert app_name is not None
        self.__app_name = app_name
        self.__environment.set_app_name(app_name)


    def get_app_name(self):
        return self.__app_name


    def set_app_version(self, app_version):
        assert app_version is not None
        self.__app_version = app_version
        self.__environment.set_app_version(app_version)


    def get_app_version(self):
        return self.__app_version


    def append(self, task):
        assert task is not None
        return self.__root_task.append(task)


    def install(self):
        self.__environment.start()
        result        = Task.success
        last_path_len = 0
        for task in self.__task_iter:
            # If we decreased the depth, decrease indent:
            change = last_path_len - self.__task_iter.current_depth()
            if change > 0:
                for i in range(change):
                    self.__environment.section_end()
            last_path_len = self.__task_iter.current_depth()

            # If the task has children, increase indent.
            if task.get(0) is not None:
                self.__environment.section_start(task.get_name())

            # Execute the task.
            self.__environment.set_task_path(self.__task_iter.current_path())
            result = task.install(self.__environment)
            if result != Task.success:
                break
        self.__environment.end()
        return result


    def uninstall(self):
        self.__environment.start()
        result        = Task.success
        last_path_len = 0
        for task in self.__task_iter:
            # If we decreased the depth, decrease indent:
            change = last_path_len - self.__task_iter.current_depth()
            if change > 0:
                for i in range(change):
                    self.__environment.section_end()
            last_path_len = self.__task_iter.current_depth()

            # If the task has children, increase indent.
            if task.get(0) is not None:
                self.__environment.section_start(task.get_name())

            # Execute the task.
            self.__environment.set_task_path(self.__task_iter.current_path())
            result = self.__root_task.uninstall(self.__environment)
            if result != Task.success:
                break
        self.__environment.end()
        return result


if __name__ == '__main__':
    import unittest
    import cgi
    from WebEnvironment       import WebEnvironment
    from LicenseAgreementTask import LicenseAgreementTask
    from Task                 import Task

    class ConstructorTest(unittest.TestCase):
        def runTest(self):
            name        = 'Test Application'
            version     = '0.1.2'
            environment = WebEnvironment(cgi.FieldStorage())
            constructor = Constructor(environment)
            constructor.set_app_name(name)
            constructor.set_app_version(version)
            assert constructor.get_app_name()    == name
            assert constructor.get_app_version() == version

            # Test running some tasks.
            la_task = LicenseAgreementTask('SERVE ME!')
            constructor.append(la_task)
            assert constructor.install() == Task.interact

    testcase = ConstructorTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
