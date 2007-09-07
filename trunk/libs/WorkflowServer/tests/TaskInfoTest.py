import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testTaskInfo']
    return unittest.TestSuite(map(TaskInfoTest, tests))

from TaskInfo import TaskInfo

class TaskInfoTest(unittest.TestCase):
    def testTaskInfo(self):
        info = TaskInfo()

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
