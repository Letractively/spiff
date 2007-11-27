import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testMkUrl']
    return unittest.TestSuite(map(MkUrlTest, tests))

from mkurl import mkurl

class MkUrlTest(unittest.TestCase):
    def testMkUrl(self):
        url = mkurl('www.debain.org', home = ['test'])
        self.assert_(url == 'www.debain.org?home=test', url)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
