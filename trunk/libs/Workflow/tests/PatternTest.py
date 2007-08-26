import sys, unittest, os
sys.path.insert(0, '..')

def suite():
    tests = ['testPattern']
    return unittest.TestSuite(map(PatternTest, tests))

from Activities        import *
from Workflow          import Workflow
from Job               import Job
from BranchNode        import *
from Storage           import XmlReader
from xml.parsers.expat import ExpatError

def print_name(job, branch_node, activity):
    reached_key = "%s_reached" % str(activity.name)
    n_reached   = job.get_attribute(reached_key, 0) + 1
    step        = job.get_attribute('step', 0) + 1
    job.set_attribute(**{reached_key: n_reached})
    job.set_attribute(two             = 2)
    job.set_attribute(three           = 3)
    job.set_attribute(step            = step)
    job.set_attribute(test_attribute1 = 'false')
    job.set_attribute(test_attribute2 = 'true')

    # Record the path in an attribute.
    current     = branch_node.find_path(None, branch_node.activity)
    depth       = len(current.split('/')) - 1
    indent      = ('  ' * depth)
    taken_path  = job.get_attribute('taken_path', '')
    taken_path += '%s%s\n' % (indent, activity.name)
    job.set_attribute(taken_path = taken_path)
    
    #print "%s%s" % (indent, activity.name)
    #print "%s%s (reached %s times)" % (indent, activity.name, n_reached)
    #print "PATH:", current, branch_node.name, branch_node.id

class PatternTest(unittest.TestCase):
    def setUp(self):
        self.reader = XmlReader()
        self.wf     = None


    def testPattern(self):
        xml_path = 'xml/patterns/'
        for filename in os.listdir(xml_path):
            if not filename.endswith('.xml'):
                continue
            xml_filename  = os.path.join(xml_path, filename)
            path_filename = os.path.join(xml_path, filename + '.path')
            file          = open(path_filename, 'r')
            expected      = file.read()
            file.close()
            try:
                workflow_list = self.reader.parse_file(xml_filename)
                self.testWorkflow(workflow_list[0], expected, filename)
            except:
                print '%s:' % xml_filename
                raise


    def testWorkflow(self, wf, expected, name):
        for activity in wf.activities:
            activity.user_func = print_name

        # Execute all activities within the Job.
        job = Job(wf)
        job.execute_all()

        #job.branch_tree.dump()

        # Check whether the correct route was taken.
        taken_path = job.get_attribute('taken_path', '')
        self.assert_(taken_path == expected,
                     '%s:\nExpected:\n%s\nbut got:\n%s\n' % (name, expected, taken_path))

        # Make sure that there are no waiting activities in the tree.
        for node in BranchNode.Iterator(job.branch_tree, BranchNode.WAITING):
            job.branch_tree.dump()
            raise Exception('Node with state WAITING: %s' % node.name)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
