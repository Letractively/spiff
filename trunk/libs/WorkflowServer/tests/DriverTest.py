import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testDriver']
    return unittest.TestSuite(map(DriverTest, tests))

from DBTest import DBTest
from Driver import Driver

class DriverTest(DBTest):
    def testDriver(self):
        driver = Driver(self.db)
        self.assert_(driver is not None)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
