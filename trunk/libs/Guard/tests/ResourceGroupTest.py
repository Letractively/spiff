import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testResourceGroup']
    return unittest.TestSuite(map(ResourceGroupTest, tests))

from ResourceGroup import ResourceGroup

class ResourceGroupTest(unittest.TestCase):
    def testResourceGroup(self):
        name  = "Test ResourceGroup"
        group = ResourceGroup(name)
        self.assert_(group.get_id()   == -1)
        self.assert_(group.get_name() == name)
        self.assert_(group.is_group() == True)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
