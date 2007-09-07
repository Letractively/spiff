import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testAction']
    return unittest.TestSuite(map(ActionTest, tests))

from Action import Action

class ActionTest(unittest.TestCase):
    def testAction(self):
        name   = "Test Action"
        action = Action(name)
        assert action.get_id()     == -1
        assert action.get_name()   == name

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
