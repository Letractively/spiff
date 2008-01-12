import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'Integrator'))

def suite():
    tests = ['testEvent']
    return unittest.TestSuite(map(EventTest, tests))

from Event import Event

class EventTest(unittest.TestCase):
    def testEvent(self):
        event_uri = 'test:/my/uri/should/work/'
        args      = 'anything'
        event     = Event(event_uri, args)
        self.assert_(event.get_uri()  == event_uri)
        self.assert_(event.get_args() == args)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
