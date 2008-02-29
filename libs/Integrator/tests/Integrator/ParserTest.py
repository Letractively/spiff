import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'Integrator'))

def suite():
    tests = ['testParser']
    return unittest.TestSuite(map(ParserTest, tests))

from Parser  import Parser
from Package import Package

class ParserTest(unittest.TestCase):
    def testParser(self):
        filename = '../samples/SpiffExtension/package.xml'
        parser   = Parser()
        package  = parser.parse_file(filename, Package)
        self.assert_(package.get_name() == 'My Spiff Extension')

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
