import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testTree']
    return unittest.TestSuite(map(BranchNodeTest, tests))

from Workflow   import Workflow
from Job        import Job
from Activities import Activity
from Exception  import WorkflowException
from BranchNode import *

class BranchNodeTest(unittest.TestCase):
    def setUp(self):
        pass


    def testTree(self):
        # Build a tree.
        wf        = Workflow()
        activity1 = Activity(wf, 'Activity 1')
        activity2 = Activity(wf, 'Activity 2')
        activity3 = Activity(wf, 'Activity 3')
        activity4 = Activity(wf, 'Activity 4')
        activity5 = Activity(wf, 'Activity 5')
        activity6 = Activity(wf, 'Activity 6')
        activity7 = Activity(wf, 'Activity 7')
        activity8 = Activity(wf, 'Activity 8')
        activity9 = Activity(wf, 'Activity 9')
        root      = BranchNode(object, activity1)
        c1        = root.add_child(activity2)
        c11       = c1.add_child(activity3)
        c111      = c11.add_child(activity4)
        c1111     = BranchNode(object, activity5, c111)
        c112      = BranchNode(object, activity6, c11)
        c12       = BranchNode(object, activity7, c1)
        c2        = BranchNode(object, activity8, root)
        c3        = BranchNode(object, activity9, root)
        c1.split()
        c3.state = COMPLETED
        c11.drop_children()

        # Check whether the tree is built properly.
        expected = """1: 1/4/BranchNode for Activity 1
  2: 1/2/BranchNode for Activity 2
    3: 1/0/BranchNode for Activity 3
    7: 1/0/BranchNode for Activity 7
  8: 1/0/BranchNode for Activity 8
  9: 4/0/BranchNode for Activity 9
  10: 1/2/BranchNode for Activity 2
    11: 1/2/BranchNode for Activity 3
      12: 1/1/BranchNode for Activity 4
        13: 1/0/BranchNode for Activity 5
      14: 1/0/BranchNode for Activity 6
    15: 1/0/BranchNode for Activity 7"""
        self.assert_(expected == root.get_dump(),
                     'Expected:\n' + expected + '\n' + \
                     'but got:\n'  + root.get_dump())

        # Now remove one line from the expected output for testing the
        # filtered iterator.
        expected2 = ''
        for line in expected.split('\n'):
            if re.search('Activity 9', line):
                continue
            expected2 += line.lstrip() + '\n'

        # Run the iterator test.
        result = ''
        for node in BranchNode.Iterator(root, WAITING):
            result += '%s: ' % node.id
            result += '%s/'  % node.state
            result += '%s/'  % len(node.children)
            result += '%s\n' % node.name
        self.assert_(expected2 == result,
                     'Expected:\n' + expected2 + '\n' + \
                     'but got:\n'  + result)

        # Some simple method tests.
        self.assert_(c1111.find_path() == '2/3/4/5', 'Invalid path: ' + c1111.find_path())
        self.assertRaises(WorkflowException, root.split)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
