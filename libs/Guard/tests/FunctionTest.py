import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testInt2Hex',
             'testMakeHandleFromString',
             'testHexPath2BinPath',
             'testBinPath2HexPath',
             'testList2BinPath',
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
        path = '012345f0'
        res  = bin_path2hex_path(hex_path2bin_path(path))
        self.assert_(res == path, res)


    def testBinPath2HexPath(self):
        self.testHexPath2BinPath()


    def testList2BinPath(self):
        path = [1, 2, 3, 4]
        res  = bin_path2list(list2bin_path(path))
        self.assert_(res == path, res)


    def testBinPath2List(self):
        self.testList2BinPath()


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
