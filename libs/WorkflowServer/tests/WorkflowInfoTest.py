import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testWorkflowInfo']
    return unittest.TestSuite(map(WorkflowInfoTest, tests))

from WorkflowInfo import WorkflowInfo

class WorkflowInfoTest(unittest.TestCase):
    def testWorkflowInfo(self):
        info = WorkflowInfo('my/handle')
        self.assert_(info.handle == 'my/handle')

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
