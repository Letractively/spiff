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
from Event     import Event
from Callback  import Callback
from threading import Thread

class EventBus(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.__pending_events = []
        self.__callbacks      = {}
        self.__next_id        = 1

    def run(self):
        while len(self.__pending_events) > 0:
            event = self.__pending_events.pop(0)
            self.emit_sync(event.get_uri(), event.get_args())

    def add_listener(self, callback):
        """
        Adds a listener to the event bus. The given function is called whenever
        any event is sent that matches the given regular expression. If no
        regular expression was given, any signal is emitted.
        @type  callback: Callback
        @param callback: Specifies the requested notification.
        @rtype:  Boolean
        @return: False if the listener was not found, True otherwise.
        """
        assert callback is not None
        self.__callbacks[str(self.__next_id)] = callback
        assert self.__next_id < sys.maxint
        self.__next_id += 1
        return self.__next_id - 1

    def remove_listener_from_id(self, id):
        """
        Removes a listener from the event bus.
        @type  id: integer
        @param id: The id of the listener to remove.
        @rtype:  Boolean
        @return: False if the listener was not found, True otherwise.
        """
        assert id > 0
        if not self.__callbacks.has_key(str(id)):
            return False
        del self.__callbacks[id]
        return True

    def emit(self, uri, args = None):
        assert uri is not None
        event = Event(uri, args)
        self.__pending_events.append(event)

    def emit_sync(self, uri, args = None):
        assert uri is not None
        for id in self.__callbacks:
            callback = self.__callbacks[id]
            if callback.matches_uri(uri):
                func     = callback.get_function()
                func(args)


if __name__ == '__main__':
    import unittest
    import time

    class EventBusTest(unittest.TestCase):
        def callback_function(self, args):
            #print 'I have been called! Fancy!'
            self.n_calls += 1

        def runTest(self):
            self.n_calls = 0
            
            # Set up a callback object.
            event_uri = 'test:/my/uri/should/work/'
            callback = Callback(self.callback_function, event_uri)
            
            # Set up the event bus.
            eb = EventBus()
            id = eb.add_listener(callback)
            assert id > 0
            
            # Try a sync call first.
            eb.emit_sync(event_uri)
            eb.emit_sync('test:non-existent/event')
            assert self.n_calls == 1
            
            # Now try that asynchronously.
            eb.emit(event_uri)
            eb.emit('test:non-existent/event')
            assert self.n_calls == 1

            # Run the queued up async events.
            eb.start()
            time.sleep(1) # The thread might need some time.
            assert self.n_calls == 2

    testcase = EventBusTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
