import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testJobInfo']
    return unittest.TestSuite(map(JobInfoTest, tests))

from JobInfo import JobInfo

class JobInfoTest(unittest.TestCase):
    def testJobInfo(self):
        info = JobInfo()

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
