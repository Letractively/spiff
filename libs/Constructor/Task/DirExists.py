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
import os.path
from Task import Task

class DirExists(Task):
    def __init__(self, dirname):
        assert dirname is not None
        Task.__init__(self, 'Checking whether ' + dirname + ' is a directory')
        self.__dirname = dirname


    def install(self, environment):
        if os.path.isdir(self.__dirname):
            return Task.success
        return Task.failure


    def uninstall(self, environment):
        return Task.success


if __name__ == '__main__':
    import unittest
    import cgi
    from ConfigParser import RawConfigParser
    from WebEnvironment import WebEnvironment

    class DirExistsTest(unittest.TestCase):
        def runTest(self):
            environment = WebEnvironment(cgi.FieldStorage())
            task        = DirExists('.')
            assert task.install(environment)   == Task.success
            assert task.uninstall(environment) == Task.success

            task        = DirExists('DefinitelyNot')
            assert task.install(environment)   == Task.failure
            assert task.uninstall(environment) == Task.success

    testcase = DirExistsTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)


