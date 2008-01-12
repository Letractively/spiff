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
from Task import Task

class CheckPythonVersion(Task):
    def __init__(self, min_version_tuple, max_version_tuple = None):
        assert min_version_tuple is not None
        Task.__init__(self, "Checking Python version")
        self.__min_version_tuple = min_version_tuple
        self.__max_version_tuple = max_version_tuple


    def install(self, environment):
        if sys.version_info < self.__min_version_tuple or \
           (self.__max_version_tuple is not None and
            sys.version_info > self.__max_version_tuple):
            self.error = 'Python version ' + sys.version + ' is not supported.'
            return Task.failure
        return Task.success


    def uninstall(self, environment):
        return Task.success


if __name__ == '__main__':
    import unittest
    import cgi
    from WebEnvironment import WebEnvironment

    class CheckPythonVersionTest(unittest.TestCase):
        def runTest(self):
            environment = WebEnvironment(cgi.FieldStorage())
            task        = CheckPythonVersion((2, 3, 0, '', 0),
                                             (2, 5, 0, '', 0))
            assert task.install(environment)   == Task.success
            assert task.uninstall(environment) == Task.success

    testcase = CheckPythonVersionTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
