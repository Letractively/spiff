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

class CreateDir(Task):
    def __init__(self, dirname, mode = 0777):
        assert dirname is not None
        assert mode    is not None
        Task.__init__(self, 'Creating directory \'%s\'' % dirname)
        self.__dirname = dirname
        self.__mode    = mode


    def install(self, environment):
        if os.path.exists(self.__dirname):
            return Task.success
        try:
            os.makedirs(self.__dirname, self.__mode)
        except:
            return Task.failure
        return Task.success


    def uninstall(self, environment):
        try:
            os.rmdir(self.__dirname)
        except:
            return Task.success
        return Task.success


if __name__ == '__main__':
    import unittest
    import cgi
    from ConfigParser import RawConfigParser
    from WebEnvironment import WebEnvironment

    class CreateDirTest(unittest.TestCase):
        def runTest(self):
            environment = WebEnvironment(cgi.FieldStorage())
            task        = CreateDir('CreateDir')
            assert task.install(environment)   == Task.success
            assert task.uninstall(environment) == Task.success

            task        = CreateDir('/CreateDirDefinitelyNot')
            assert task.install(environment)   == Task.failure
            assert task.uninstall(environment) == Task.success

    testcase = CreateDirTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)

