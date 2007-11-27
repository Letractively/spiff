import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testParseQuery']
    return unittest.TestSuite(map(ParseQueryTest, tests))

from parse_query import parse_query

urls = {
  '':                                    {},
  '?':                                   {},
  'myvar=testvalue':                     {'myvar':  ['testvalue']},
  'myvar=testvalue&myvar2=test%202':     {'myvar':  ['testvalue'],
                                          'myvar2': ['test 2']},
  'myvar=testvalue&amp;myvar2=test%202': {'myvar':  ['testvalue'],
                                          'myvar2': ['test 2']},
}

def equals(dict1, dict2):
    for k in dict1:
        if dict1.get(k) != dict2.get(k):
            return False
        if dict1.get(k)[0] != dict2.get(k)[0]:
            return False
    for k in dict2:
        if dict1.get(k) != dict2.get(k):
            return False
        if dict1.get(k)[0] != dict2.get(k)[0]:
            return False
    return True

class ParseQueryTest(unittest.TestCase):
    def testParseQuery(self):
        for url, expected in urls.iteritems():
            result = parse_query(url)
            self.assert_(equals(result, expected),
                         '%s is not %s' % (url, result))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
