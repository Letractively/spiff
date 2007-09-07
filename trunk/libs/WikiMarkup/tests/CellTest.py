import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testCell']
    return unittest.TestSuite(map(CellTest, tests))

from Cell import Cell

class CellTest(unittest.TestCase):
    def testCell(self):
        cell = Cell()

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
