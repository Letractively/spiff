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

class InteractionResult:
    def __init__(self):
        self.__values = {}


    def set(self, key, value):
        assert key is not None
        self.__values[key] = value

    
    def get(self, key):
        assert key is not None
        return self.__values[key]


if __name__ == '__main__':
    import unittest

    class InteractionResultTest(unittest.TestCase):
        def runTest(self):
            result = InteractionResult()
            result.set('test', 'testval')
            assert result.get('test') == 'testval'

    testcase = InteractionResultTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
