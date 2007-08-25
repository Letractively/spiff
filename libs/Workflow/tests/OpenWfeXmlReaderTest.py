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


    def print_name(self, job, branch_node, activity):
        print_name(job, branch_node, activity)
        job.set_attribute(test_attribute1 = 'false')
        job.set_attribute(test_attribute2 = 'true')
        self.path = job.get_attribute('taken_path')


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
                          'xml/test_workflow_empty1.xml')

        # File containing only "<xml></xml>".
        self.reader.parse_file('xml/test_workflow_empty2.xml')

        # Read a complete workflow.
        self.reader.parse_file('xml/test_openwfe_workflow_1.xml')


    def testRunWorkflow(self):
        wf = self.reader.parse_file('xml/test_openwfe_workflow_1.xml')

        for activity in wf[0].activities:
            activity.user_func = self.print_name

        job = Job(wf[0])
        try:
            job.execute_all()
        except:
            job.branch_tree.dump()
            raise

        path = [(1, 'Start'),
                (1, 'concurrence_1'),
                (4, 'activity_a1'),
                (4, 'activity_a2'),
                (4, 'if_condition_1'),
                (4, 'activity_a3'),
                (4, 'if_condition_1_end'),
                (4, 'if_condition_2'),
                (4, 'activity_a5'),
                (4, 'if_condition_2_end'),
                (5, 'activity_b1'),
                (5, 'activity_b2'),
                (5, 'concurrence_1_end'),
                (5, 'activity_c1'),
                (5, 'activity_c2'),
                (5, 'End')]

        # Check whether the correct route was taken.
        for i, (branch_node, name) in enumerate(path):
            self.assert_(i < len(self.path),
                         'Taken route is too short: %s' % self.path)
            self.assert_(name == self.path[i][1],
                         'Incorrect route taken at %s: %s' % (name, self.path))
        self.assert_(len(self.path) == len(path),
                     'Taken route is too long: %s' % self.path)

        # Check whether all activities were in the correct branch_node.
        for i, (branch_node, name) in enumerate(path):
            self.assert_(branch_node == self.path[i][0],
                         '%s in incorrect branch_node %s: %s' % (name, branch_node, self.path))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
