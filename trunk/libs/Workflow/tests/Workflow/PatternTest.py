import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'Workflow'))

def suite():
    tests = ['testPattern']
    return unittest.TestSuite(map(PatternTest, tests))

from Tasks             import *
from Workflow          import Workflow
from Job               import Job
from BranchNode        import *
from Storage           import XmlReader
from xml.parsers.expat import ExpatError

def assign_print_name(branch_node, task):
    # In workflows that load a subworkflow, the newly loaded children
    # will not have print_name() assigned. By using this function, we
    # re-assign the function in every step, thus making sure that new
    # children also call print_name().
    for child in branch_node.children:
        child.task.pre_func  = print_name
        child.task.post_func = assign_print_name

def print_name(branch_node, task):
    job         = branch_node.job
    reached_key = "%s_reached" % str(task.name)
    n_reached   = job.get_attribute(reached_key, 0) + 1
    job.set_attribute(**{reached_key: n_reached})
    job.set_attribute(two             = 2)
    job.set_attribute(three           = 3)
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

    # Collect a list of all attributes.
    atts  = []
    for key in job.attributes:
        if key in ['data',
                   'taken_path',
                   'two',
                   'three',
                   'test_attribute1',
                   'test_attribute2']:
            continue
        if key.endswith('reached'):
            continue
        atts.append('%s=%s' % (key, job.get_attribute(key)))

    # Collect a list of all task properties.
    props = []
    for key in task.properties:
        props.append('%s=%s' % (key, task.get_attribute(key)))

    # Store the list of attributes and properties in the job.
    data  = job.get_attribute('data', '')
    data += task.name + ': ' + ';'.join(atts) + '/' + ';'.join(props) + '\n'
    job.set_attribute(data = data)
    
    #print "%s%s" % (indent, task.name)
    #print "REACHED:", reached_key, n_reached
    #print "%s%s (reached %s times)" % (indent, task.name, n_reached)
    #print "PATH:", current, branch_node.name, branch_node.id

    return True

class PatternTest(unittest.TestCase):
    def setUp(self):
        self.xml_path = ['xml/spiff/control-flow/',
                         'xml/spiff/data/',
                         'xml/spiff/resource/']
        self.reader   = XmlReader()
        self.wf       = None


    def testPattern(self):
        for dirname in self.xml_path:
            dirname = os.path.join(os.path.dirname(__file__), dirname)
            for filename in os.listdir(dirname):
                if not filename.endswith('.xml'):
                    continue
                self.testFile(os.path.join(dirname, filename))


    def testFile(self, xml_filename):
        try:
            #print '\n%s: ok' % xml_filename,
            workflow_list = self.reader.parse_file(xml_filename)
            self.testWorkflow(workflow_list[0], xml_filename)
        except:
            print '%s:' % xml_filename
            raise


    def testWorkflow(self, wf, xml_filename):
        for name in wf.tasks:
            wf.tasks[name].pre_func  = print_name
            wf.tasks[name].post_func = assign_print_name

        job = Job(wf)
        self.assert_(not job.is_completed(),
                     'Job is not complete before start')

        # Execute all tasks within the Job.
        try:
            job.execute_all(False)
        except:
            job.branch_tree.dump()
            raise

        #job.branch_tree.dump()
        self.assert_(job.is_completed(),
                     'execute_all() returned, but job is not complete')

        # Make sure that there are no waiting tasks left in the tree.
        for node in BranchNode.Iterator(job.branch_tree, BranchNode.WAITING):
            job.branch_tree.dump()
            raise Exception('Node with state WAITING: %s' % node.name)

        # Check whether the correct route was taken.
        filename = xml_filename + '.path'
        if os.path.exists(filename):
            file     = open(filename, 'r')
            expected = file.read()
            file.close()
            taken_path = job.get_attribute('taken_path', '')
            error      = '%s:\n'       % name
            error     += 'Expected:\n'
            error     += '%s\n'        % expected
            error     += 'but got:\n'
            error     += '%s\n'        % taken_path
            self.assert_(taken_path == expected, error)

        # Check attribute availibility.
        filename = xml_filename + '.data'
        if os.path.exists(filename):
            file     = open(filename, 'r')
            expected = file.read()
            file.close()
            result   = job.get_attribute('data', '')
            error    = '%s:\n'       % name
            error   += 'Expected:\n'
            error   += '%s\n'        % expected
            error   += 'but got:\n'
            error   += '%s\n'        % result
            self.assert_(result == expected, error)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        test = PatternTest('testFile')
        test.setUp()
        test.testFile(sys.argv[1])
        sys.exit(0)
    unittest.TextTestRunner(verbosity = 2).run(suite())
