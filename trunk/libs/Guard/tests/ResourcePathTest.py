import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testResourcePath']
    return unittest.TestSuite(map(ResourcePathTest, tests))

from ResourcePath import ResourcePath

class ResourcePathTest(unittest.TestCase):
    def testResourcePath(self):
        path = ResourcePath('0/1/2')
        #FIXME

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
