import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'WorkflowServer'))

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
