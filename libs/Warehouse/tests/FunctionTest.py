import sys, unittest, re
sys.path.insert(0, '..')

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
