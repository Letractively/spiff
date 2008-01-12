import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'Integrator'))

def suite():
    tests = ['testCallback']
    return unittest.TestSuite(map(CallbackTest, tests))

from Callback import Callback

class CallbackTest(unittest.TestCase):
    def callback_function(self):
        pass
        
    def testCallback(self):
        event_uri = 'test:/my/uri/should/work/'
        callback = Callback(self.callback_function)
        assert callback.get_function()  == self.callback_function
        assert callback.get_event_uri() == None
        assert callback.matches_uri(event_uri)
        assert callback.matches_uri('asdasd')
        
        callback = Callback(self.callback_function, event_uri)
        assert callback.get_function()  == self.callback_function
        assert callback.get_event_uri() == event_uri
        assert callback.matches_uri(event_uri)
        assert not callback.matches_uri('asdasd')

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
