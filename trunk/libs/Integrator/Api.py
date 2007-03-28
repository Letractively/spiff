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
from EventBus  import EventBus
from Callback  import Callback
from functions import is_valid_uri

class Api:
    def __init__(self):
        self._event_bus = EventBus()
        self._manager   = None


    def activate(self, manager):
        assert manager is not None
        self._manager = manager
        self._on_api_activate()


    def _on_api_activate(self):
        """
        May be overwritten.
        """
        pass


    def add_listener(self, func, uri = None):
        assert is_valid_uri(uri)
        #FIXME: Check permissions!
        callback = Callback(func, uri)
        return self._event_bus.add_listener(callback)

        
    def __emit(self, uri, args, synchronous):
        assert is_valid_uri(uri)
        #FIXME: Check signal permissions!
        self._manager.load_extension_from_event(uri)
        if synchronous:
            self._event_bus.emit_sync(uri, args)
        else:
            self._event_bus.emit(uri, args)


    def emit(self, uri, args = None):
        return self.__emit(uri, args, False)


    def emit_sync(self, uri, args = None):
        return self.__emit(uri, args, True)


if __name__ == '__main__':
    import unittest
    from Manager  import Manager
    from EventBus import EventBus

    class ApiTest(unittest.TestCase):
        def dummy(self):
            pass

        def runTest(self):
            eb  = EventBus()
            api = Api()
            assert api.add_listener(self.dummy, "test:some/event/uri") >= 0

            #Note: The other functions are not tested here, but in the
            #test of the Manager class, whose constructor instantiates an
            #Api object.

    testcase = ApiTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
