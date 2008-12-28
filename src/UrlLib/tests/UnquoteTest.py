import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testUnquote']
    return unittest.TestSuite(map(UnquoteTest, tests))

from unquote import unquote

strings = {
  'myvar=testvalue&amp;myvar2=test%202':
      'myvar=testvalue&amp;myvar2=test 2',
}

class UnquoteTest(unittest.TestCase):
    def testUnquote(self):
        for string, expected in strings.iteritems():
            result = unquote(string)
            self.assert_(result == expected,
                         '%s is %s' % (string, result))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())

