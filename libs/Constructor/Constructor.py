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

class Constructor:
    def __init__(self, app_name, app_version = ''):
        assert app_name    is not None
        assert app_version is not None
        self.__app_name    = app_name
        self.__app_version = app_version


    def get_app_name(self):
        return self.__app_name


    def get_app_version(self):
        return self.__app_version


if __name__ == '__main__':
    import unittest

    class ConstructorTest(unittest.TestCase):
        def runTest(self):
            name        = 'Test Application'
            version     = '0.1.2'
            constructor = Constructor(name, version)
            assert constructor.get_app_name()    == name
            assert constructor.get_app_version() == version

    testcase = ConstructorTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)