import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testInt2Hex',
             'testMakeHandleFromString',
             'testHexPath2BinPath',
             'testBinPath2HexPath',
             'testBinPath2List']
    return unittest.TestSuite(map(FunctionTest, tests))

from functions import *

class FunctionTest(unittest.TestCase):
    def testInt2Hex(self):
        self.assert_(int2hex(10, 8) == '0000000a')


    def testMakeHandleFromString(self):
        foo = 'Some Weird 123 String, with %$[]\/ Stuff'
        bar = 'some_weird_123_string_with_/_stuff'
        res = make_handle_from_string(foo)
        self.assert_(res == bar)
        res = make_handle_from_string(bar)
        self.assert_(res == bar)


    def testHexPath2BinPath(self):
        pass #FIXME


    def testBinPath2HexPath(self):
        pass #FIXME


    def testBinPath2List(self):
        pass #FIXME

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
