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

class Api:
    def __init__(self, manager, event_bus):
        assert manager   is not None
        assert event_bus is not None
        self.__manager   = manager
        self.__event_bus = event_bus

    def emit(self, uri, args, synchronous = False):
        #FIXME: Check signal permissions!
        self.__manager.load_extension_from_event(uri)
        if synchronous:
            self.__event_bus.emit_sync(uri, args)
        else:
            self.__event_bus.emit(uri, args)


if __name__ == '__main__':
    import unittest

    class ApiTest(unittest.TestCase):
        def runTest(self):
            #FIXME: Implement test.
            pass
            
    testcase = ApiTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
