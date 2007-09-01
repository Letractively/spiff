import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testTree']
    return unittest.TestSuite(map(BranchNodeTest, tests))

from Workflow   import Workflow
from Job        import Job
from Tasks import Task
from Exception  import WorkflowException
from BranchNode import *

class BranchNodeTest(unittest.TestCase):
    def setUp(self):
        pass


    def testTree(self):
        # Build a tree.
        wf        = Workflow()
        task1 = Task(wf, 'Task 1')
        task2 = Task(wf, 'Task 2')
        task3 = Task(wf, 'Task 3')
        task4 = Task(wf, 'Task 4')
        task5 = Task(wf, 'Task 5')
        task6 = Task(wf, 'Task 6')
        task7 = Task(wf, 'Task 7')
        task8 = Task(wf, 'Task 8')
        task9 = Task(wf, 'Task 9')
        root      = BranchNode(object, task1)
        c1        = root.add_child(task2)
        c11       = c1.add_child(task3)
        c111      = c11.add_child(task4)
        c1111     = BranchNode(object, task5, c111)
        c112      = BranchNode(object, task6, c11)
        c12       = BranchNode(object, task7, c1)
        c2        = BranchNode(object, task8, root)
        c3        = BranchNode(object, task9, root)
        c1.split()
        c3.state = BranchNode.COMPLETED
        c11.drop_children()

        # Check whether the tree is built properly.
        expected = """1/0: BranchNode for Task 1 State: 1 Children: 4
  2/0: BranchNode for Task 2 State: 1 Children: 2
    3/0: BranchNode for Task 3 State: 1 Children: 0
    7/0: BranchNode for Task 7 State: 1 Children: 0
  8/0: BranchNode for Task 8 State: 1 Children: 0
  9/0: BranchNode for Task 9 State: 4 Children: 0
  10/0: BranchNode for Task 2 State: 1 Children: 2
    11/0: BranchNode for Task 3 State: 1 Children: 2
      12/0: BranchNode for Task 4 State: 1 Children: 1
        13/0: BranchNode for Task 5 State: 1 Children: 0
      14/0: BranchNode for Task 6 State: 1 Children: 0
    15/0: BranchNode for Task 7 State: 1 Children: 0"""
        self.assert_(expected == root.get_dump(),
                     'Expected:\n' + expected + '\n' + \
                     'but got:\n'  + root.get_dump())

        # Now remove one line from the expected output for testing the
        # filtered iterator.
        expected2 = ''
        for line in expected.split('\n'):
            if re.search('Task 9', line):
                continue
            expected2 += line.lstrip() + '\n'

        # Run the iterator test.
        result = ''
        for node in BranchNode.Iterator(root, BranchNode.WAITING):
            result += '%s/'             % node.id
            result += '%s:'             % node.thread_id
            result += ' %s'             % node.name
            result += ' State: %s'      % node.state
            result += ' Children: %s\n' % len(node.children)
        self.assert_(expected2 == result,
                     'Expected:\n' + expected2 + '\n' + \
                     'but got:\n'  + result)

        # Some simple method tests.
        self.assertRaises(WorkflowException, root.split)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
