import sys
sys.path.append('..')
from DocumentModel import *
from Plex          import *

class PythonFile(File):
    def load(self, filename):
        fd = file.open(filename)
        #FIXME


if __name__ == '__main__':
    import unittest

    class PythonFileTest(unittest.TestCase):
        def runTest(self):
            filename  = 'test.python'
            
    testcase = PythonFileTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
