import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'Integrator'))

def suite():
    tests = ['testEventBus']
    return unittest.TestSuite(map(EventBusTest, tests))

import time
from Callback import Callback
from EventBus import EventBus

class EventBusTest(unittest.TestCase):
    def callback_function(self, args):
        #print 'I have been called! Fancy!'
        self.n_calls += 1

    def testEventBus(self):
        self.n_calls = 0
        
        # Set up a callback object.
        event_uri = 'test:/my/uri/should/work/'
        callback = Callback(self.callback_function, event_uri)
        
        # Set up the event bus.
        eb = EventBus()
        id = eb.add_listener(callback)
        self.assert_(id > 0)
        
        # Try a sync call first.
        eb.emit_sync(event_uri)
        eb.emit_sync('test:non-existent/event')
        self.assert_(self.n_calls == 1)
        
        # Now try that asynchronously.
        eb.emit(event_uri)
        eb.emit('test:non-existent/event')
        self.assert_(self.n_calls == 1)

        # Run the queued up async events.
        eb.start()
        time.sleep(1) # The thread might need some time.
        self.assert_(self.n_calls == 2)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
