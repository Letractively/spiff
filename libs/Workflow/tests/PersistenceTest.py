import os, sys, unittest
sys.path.insert(0, '..')

def suite():
    tests = ['testPickle']
    return unittest.TestSuite(map(PersistenceTest, tests))

import pickle, pprint
from random       import randint
from WorkflowTest import WorkflowTest, print_name
from Job          import Job
from Storage      import XmlReader

class PersistenceTest(WorkflowTest):
    def setUp(self):
        WorkflowTest.setUp(self)
        self.reader = XmlReader()
        self.data_file = 'data.pkl'


    def testPickleSingle(self, workflow, job):
        # Execute a random number of steps.
        for i in xrange(randint(0, len(workflow.tasks))):
            job.execute_next()
    
        # Store the workflow instance in a file.
        output = open(self.data_file, 'wb')
        pickle.dump(job, output, -1)
        output.close()

        # Load the workflow instance from a file and delete the file.
        input = open(self.data_file, 'rb')
        job   = pickle.load(input)
        input.close()
        os.remove(self.data_file)

        # Run the rest of the workflow.
        job.execute_all()

        # Check whether the correct route was taken.
        taken_path = job.get_attribute('taken_path', [])
        for i, (branch, name) in enumerate(self.expected_path):
            self.assert_(i < len(taken_path),
                         'Taken route is too short: %s' % taken_path)
            self.assert_(name == taken_path[i][1],
                         'Incorrect route taken at step %s (%s):\n%s' % (i + 1, taken_path[i][1], self.format_path(taken_path)))
        self.assert_(len(taken_path) == len(self.expected_path),
                     'Taken route is too long: %s' % taken_path)

    def testPickle(self):
        # Read a complete workflow.
        workflow_list = self.reader.parse_file('xml/workflow1.xml')
        for name in workflow_list[0].tasks:
            workflow_list[0].tasks[name].user_func = print_name

        for i in xrange(5):
            job = Job(workflow_list[0])
            self.testPickleSingle(workflow_list[0], job)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
