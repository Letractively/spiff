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
class Callback:
    def  __init__(self, name, context = None):
        assert name is not None
        self.__name    = name
        self.__context = context

    def get_name(self):
        return self.__name

    def get_context(self):
        return self.__context


if __name__ == '__main__':
    import unittest

    class CallbackTest(unittest.TestCase):
        def runTest(self):
            name     = 'Test Callback'
            context  = 'Test Context'
            callback = Callback(name)
            assert callback.get_name()    == name
            assert callback.get_context() == None
            
            callback = Callback(name, context)
            assert callback.get_name()    == name
            assert callback.get_context() == context

    testcase = CallbackTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
