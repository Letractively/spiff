import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testParseUrl']
    return unittest.TestSuite(map(ParseUrlTest, tests))

from parse_url      import parse_url
from ParseQueryTest import equals

urls = {
  'testhost':
      ('http',
       None,
       None,
       'testhost',
       {}),
  'testhost?myvar=testvalue':
      ('http',
       None,
       None,
       'testhost',
       {'myvar': ['testvalue']}),
  'user@testhost':
      ('http',
       'user',
       None,
       'testhost',
       {}),
  'user@testhost?myvar=testvalue':
      ('http',
       'user',
       None,
       'testhost',
       {'myvar': ['testvalue']}),
  'user:mypass@testhost':
      ('http',
       'user',
       'mypass',
       'testhost',
       {}),
  'user:mypass@testhost?myvar=testvalue':
      ('http',
       'user',
       'mypass',
       'testhost',
       {'myvar': ['testvalue']}),
  'ssh:testhost':
      ('ssh',
       None,
       None,
       'testhost',
       {}),
  'ssh:testhost?myvar=testvalue':
      ('ssh',
       None,
       None,
       'testhost',
       {'myvar': ['testvalue']}),
  'ssh://testhost':
      ('ssh',
       None,
       None,
       'testhost',
       {}),
  'ssh://testhost?myvar=testvalue':
      ('ssh',
       None,
       None,
       'testhost',
       {'myvar': ['testvalue']}),
  'ssh://user@testhost':
      ('ssh',
       'user',
       None,
       'testhost',
       {}),
  'ssh://user@testhost?myvar=testvalue':
      ('ssh',
       'user',
       None,
       'testhost',
       {'myvar': ['testvalue']}),
  'ssh://user:password@testhost':
      ('ssh',
       'user',
       'password',
       'testhost',
       {}),
  'ssh://user:password@testhost?myvar=testvalue':
      ('ssh',
       'user',
       'password',
       'testhost',
       {'myvar': ['testvalue']}),
  'ssh://user:password@testhost?myvar=testvalue&myvar2=test%202':
      ('ssh',
       'user',
       'password',
       'testhost',
       {'myvar': ['testvalue'], 'myvar2': ['test 2']}),
  'ssh://user:password@testhost?myvar=testvalue&amp;myvar2=test%202':
      ('ssh',
       'user',
       'password',
       'testhost',
       {'myvar': ['testvalue'], 'myvar2': ['test 2']})
}

class ParseUrlTest(unittest.TestCase):
    def testParseUrl(self):
        for url in urls:
            #print "-------------", url, "------------"
            result = parse_url(url)
            #print "RESULT:", result
            proto1, user1, passwd1, host1, query1 = parse_url(url)
            proto2, user2, passwd2, host2, query2 = urls.get(url)
            self.assert_(proto1  == proto2,  proto1)
            self.assert_(user1   == user2,   user1)
            self.assert_(passwd1 == passwd2, passwd1)
            self.assert_(host1   == host2,   host1)
            self.assert_(equals(query1, query2),
                         '%s is not %s' % (url, query1))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
