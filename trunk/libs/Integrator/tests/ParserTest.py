import sys, unittest, re
sys.path.insert(0, '..')
sys.path.insert(0, '../..')

def suite():
    tests = ['testParser']
    return unittest.TestSuite(map(ParserTest, tests))

from Parser import Parser

class ParserTest(unittest.TestCase):
    def testParser(self):
        filename = '../samples/SpiffExtension/Extension.xml'
        parser   = Parser()
        parser.parse_file(filename)
        self.assert_(parser.package.get_name() == 'My Spiff Extension')

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
