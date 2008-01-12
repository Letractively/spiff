import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'Integrator'))

def suite():
    tests = ['testApi']
    return unittest.TestSuite(map(ApiTest, tests))

from Api      import Api
from EventBus import EventBus

class ApiTest(unittest.TestCase):
    def testApi(self):
        eb  = EventBus()
        api = Api()

        #Note: Methods are not tested here, but in the
        #test of the Manager class, whose constructor instantiates an
        #Api object.

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())