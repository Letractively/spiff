import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testResourceSection']
    return unittest.TestSuite(map(ResourceSectionTest, tests))

from ResourceSection import ResourceSection

class ResourceSectionTest(unittest.TestCase):
    def testResourceSection(self):
        name   = "Test ResourceSection"
        section = ResourceSection(name)
        self.assert_(section.get_id()   == -1)
        self.assert_(section.get_name() == name)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
