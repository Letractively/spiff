import sys, unittest, os
sys.path.insert(0, '..')

def suite():
    tests = ['testPattern']
    return unittest.TestSuite(map(PatternTest, tests))

from Tasks        import *
from Workflow          import Workflow
from Job               import Job
from BranchNode        import *
from Storage           import XmlReader
from xml.parsers.expat import ExpatError

def print_name(job, branch_node, task):
    reached_key = "%s_reached" % str(task.name)
    n_reached   = job.get_attribute(reached_key, 1) + 1
    step        = job.get_attribute('step', 1) + 1
    job.set_attribute(**{reached_key: n_reached})
    job.set_attribute(two             = 2)
    job.set_attribute(three           = 3)
    job.set_attribute(step            = step)
    job.set_attribute(test_attribute1 = 'false')
    job.set_attribute(test_attribute2 = 'true')

    # Record the path in an attribute.
    depth = 0
    node  = branch_node.parent
    while node is not None:
        node   = node.parent
        depth += 1
    indent      = ('  ' * (depth - 1))
    taken_path  = job.get_attribute('taken_path', '')
    taken_path += '%s%s\n' % (indent, task.name)
    job.set_attribute(taken_path = taken_path)
    
    #print "%s%s" % (indent, task.name)
    #print "%s%s (reached %s times)" % (indent, task.name, n_reached)
    #print "PATH:", current, branch_node.name, branch_node.id
    return True

class PatternTest(unittest.TestCase):
    def setUp(self):
        self.xml_path = 'xml/patterns/'
        self.reader   = XmlReader()
        self.wf       = None


    def testPattern(self):
        for filename in os.listdir(self.xml_path):
            if not filename.endswith('.xml'):
                continue
            self.testFile(filename)


    def testFile(self, filename):
        xml_filename  = os.path.join(self.xml_path, filename)
        path_filename = os.path.join(self.xml_path, filename + '.path')
        file          = open(path_filename, 'r')
        expected      = file.read()
        file.close()
        try:
            #print '\n%s: ok' % xml_filename,
            workflow_list = self.reader.parse_file(xml_filename)
            self.testWorkflow(workflow_list[0], expected, filename)
        except:
            print '%s:' % xml_filename
            raise


    def testWorkflow(self, wf, expected, name):
        for name in wf.tasks:
            wf.tasks[name].user_func = print_name

        # Execute all tasks within the Job.
        job = Job(wf)
        job.execute_all(False)

        #job.branch_tree.dump()

        # Check whether the correct route was taken.
        taken_path = job.get_attribute('taken_path', '')
        self.assert_(taken_path == expected,
                     '%s:\nExpected:\n%s\nbut got:\n%s\n' % (name, expected, taken_path))

        # Make sure that there are no waiting tasks in the tree.
        for node in BranchNode.Iterator(job.branch_tree, BranchNode.WAITING):
            job.branch_tree.dump()
            raise Exception('Node with state WAITING: %s' % node.name)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        test = PatternTest('testFile')
        test.setUp()
        test.testFile(sys.argv[1])
        sys.exit(0)
    unittest.TextTestRunner(verbosity = 2).run(suite())
