import sys, unittest
sys.path.insert(0, '..')

def suite():
    tests = ['testParseString', 'testParseFile', 'testRunWorkflow']
    return unittest.TestSuite(map(OpenWfeXmlReaderTest, tests))

from Storage           import OpenWfeXmlReader
from Job               import Job
from xml.parsers.expat import ExpatError

class OpenWfeXmlReaderTest(unittest.TestCase):
    def setUp(self):
        self.reader = OpenWfeXmlReader()
        self.path   = []


    def print_name(self, job, branch, activity):
        job.set_attribute(test_attribute1 = 'false')
        job.set_attribute(test_attribute2 = 'true')
        self.path.append((branch.id, activity.name))


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
        job.execute_all()

        path = [(1, 'Start'),
                (1, 'concurrence_1'),
                (3, 'activity_b1'),
                (2, 'activity_a1'),
                (3, 'activity_b2'),
                (2, 'activity_a2'),
                (2, 'if_condition_1'),
                (2, 'activity_a3'),
                (2, 'if_condition_1'),
                (2, 'if_condition_2'),
                (2, 'activity_a5'),
                (2, 'if_condition_2'),
                (2, 'concurrence_1'),
                (2, 'activity_c1'),
                (2, 'activity_c2')]

        # Check whether the correct route was taken.
        for i, (branch, name) in enumerate(path):
            self.assert_(i < len(self.path),
                         'Taken route is too short: %s' % self.path)
            self.assert_(name == self.path[i][1],
                         'Incorrect route taken at %s: %s' % (name, self.path))
        self.assert_(len(self.path) == len(path),
                     'Taken route is too long: %s' % self.path)

        # Check whether all activities were in the correct branch.
        for i, (branch, name) in enumerate(path):
            self.assert_(branch == self.path[i][0],
                         '%s in incorrect branch %s: %s' % (name, branch, self.path))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
