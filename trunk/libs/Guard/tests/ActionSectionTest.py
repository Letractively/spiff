import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testActionSection']
    return unittest.TestSuite(map(ActionSectionTest, tests))

from ActionSection import ActionSection

class ActionSectionTest(unittest.TestCase):
    def testActionSection(self):
        name   = "Test ActionSection"
        section = ActionSection(name)
        assert section.get_id()   == -1
        assert section.get_name() == name

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
