import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'Warehouse'))

def suite():
    tests = ['testRandomString',
             'testRandomPath']
    return unittest.TestSuite(map(FunctionTest, tests))

from functions import *

class FunctionTest(unittest.TestCase):
    def testRandomString(self):
        pass #FIXME


    def testRandomPath(self):
        pass #FIXME

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
