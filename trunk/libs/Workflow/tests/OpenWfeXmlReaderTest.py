import sys, unittest
sys.path.insert(0, '..')

def suite():
    tests = ['testParseString', 'testParseFile', 'testRunWorkflow']
    return unittest.TestSuite(map(OpenWfeXmlReaderTest, tests))

from WorkflowTest      import print_name
from Storage           import OpenWfeXmlReader
from Job               import Job
from xml.parsers.expat import ExpatError

class OpenWfeXmlReaderTest(unittest.TestCase):
    def setUp(self):
        self.reader = OpenWfeXmlReader()
        self.path   = []


    def print_name(self, branch_node, task):
        print_name(branch_node, task)
        branch_node.job.set_attribute(test_attribute1 = 'false')
        branch_node.job.set_attribute(test_attribute2 = 'true')
        self.path = branch_node.job.get_attribute('taken_path')
        return True


    def testParseString(self):
        self.assertRaises(ExpatError,
                          self.reader.parse_string,
                          '')
        self.reader.parse_string('<xml></xml>')


    def testParseFile(self):
        # File not found.
        self.assertRaises(IOError,
                          self.reader.parse_file,
                          'foo')

        # 0 byte sized file.
        self.assertRaises(ExpatError,
                          self.reader.parse_file,
                          'xml/empty1.xml')

        # File containing only "<xml></xml>".
        self.reader.parse_file('xml/empty2.xml')

        # Read a complete workflow.
        self.reader.parse_file('xml/openwfe/workflow1.xml')


    def testRunWorkflow(self):
        wf = self.reader.parse_file('xml/openwfe/workflow1.xml')

        for name in wf[0].tasks:
            wf[0].tasks[name].user_func = self.print_name

        job = Job(wf[0])
        try:
            job.execute_all()
        except:
            job.branch_tree.dump()
            raise

        path = [(0, 'Start'),
                (0, 'concurrence_1'),
                (0, 'task_a1'),
                (0, 'task_a2'),
                (0, 'if_condition_1'),
                (0, 'task_a3'),
                (0, 'if_condition_1_end'),
                (0, 'if_condition_2'),
                (0, 'task_a5'),
                (0, 'if_condition_2_end'),
                (0, 'task_b1'),
                (0, 'task_b2'),
                (0, 'concurrence_1_end'),
                (0, 'task_c1'),
                (0, 'task_c2'),
                (0, 'End')]

        # Check whether the correct route was taken.
        for i, (branch_node, name) in enumerate(path):
            self.assert_(i < len(self.path),
                         'Taken route is too short: %s' % self.path)
            self.assert_(name == self.path[i][1],
                         'Incorrect route taken at %s: %s' % (name, self.path))
        self.assert_(len(self.path) == len(path),
                     'Taken route is too long: %s' % self.path)

        # Check whether all tasks were in the correct branch_node.
        for i, (branch_node, name) in enumerate(path):
            self.assert_(branch_node == self.path[i][0],
                         '%s in incorrect branch_node %s: %s' % (name, branch_node, self.path))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
