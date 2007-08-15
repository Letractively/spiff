import sys, unittest
sys.path.insert(0, '..')

def suite():
    tests = ['testParseString', 'testParseFile', 'testRunWorkflow']
    return unittest.TestSuite(map(XmlReaderTest, tests))

from WorkflowTest      import WorkflowTest
from Storage           import XmlReader
from xml.parsers.expat import ExpatError

class XmlReaderTest(WorkflowTest):
    def setUp(self):
        WorkflowTest.setUp(self)
        self.reader = XmlReader()


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
        self.reader.parse_file('xml/test_workflow_1.xml')


    def testRunWorkflow(self):
        workflow_list = self.reader.parse_file('xml/test_workflow_1.xml')
        for wf in workflow_list:
            self.runWorkflow(wf)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
