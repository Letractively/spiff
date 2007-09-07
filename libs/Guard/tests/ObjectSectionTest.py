import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testObjectSection']
    return unittest.TestSuite(map(ObjectSectionTest, tests))

from ObjectSection import ObjectSection

class ObjectSectionTest(unittest.TestCase):
    def testObjectSection(self):
        name   = "Test ObjectSection"
        section = ObjectSection(name)
        self.assert_(section.get_id()   == -1)
        self.assert_(section.get_name() == name)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
