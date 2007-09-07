import sys, unittest, re
sys.path.insert(0, '..')
sys.path.insert(0, '../..')

def suite():
    tests = ['testEvent']
    return unittest.TestSuite(map(EventTest, tests))

from Event import Event

class EventTest(unittest.TestCase):
    def testEvent(self):
        event_uri = 'test:/my/uri/should/work/'
        args      = 'anything'
        event = Event(event_uri, args)
        self.assert_(event.get_uri()  == event_uri)
        self.assert_(event.get_args() == args)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
