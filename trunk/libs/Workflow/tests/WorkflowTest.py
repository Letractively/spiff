import sys, unittest
sys.path.insert(0, '..')

def suite():
    tests = ['testWorkflow']
    return unittest.TestSuite(map(WorkflowTest, tests))

from Activities import *
from Workflow   import Workflow
from Job        import Job

class WorkflowTest(unittest.TestCase):
    """
    WARNING: Make sure to keep this test in sync with XmlReaderTest! Any
    change will break both tests!
    """
    def setUp(self):
        self.wf   = Workflow()
        self.path = []


    def print_name(self, job, branch, activity):
        reached_key = "%s_reached" % str(activity.name)
        n_reached   = job.get_attribute(reached_key, 0) + 1
        step        = job.get_attribute('step', 0) + 1
        job.set_attribute(**{reached_key: n_reached})
        job.set_attribute(two             = 2)
        job.set_attribute(three           = 3)
        job.set_attribute(step            = step)
        job.set_attribute(test_attribute1 = 'false')
        job.set_attribute(test_attribute2 = 'true')
        #print "%s. Branch %s: %s reached %s times" % (step, branch.id, activity.name, n_reached)
        self.path.append((branch.id, activity.name))


    def format_path(self, path):
        """
        Format a path for printing.
        
        path -- list containing tuples.
        """
        string = ''
        for i, (branch, name) in enumerate(path):
            string += "%s. Branch %s: %s\n" % (i + 1, branch, name)
        return string


    def testWorkflow(self):
        # Build one branch.
        a1 = Activity(self.wf, "activity_a1")
        self.wf.start.connect(a1)

        a2 = Activity(self.wf, "activity_a2")
        a1.connect(a2)

        # Build another branch.
        b1 = Activity(self.wf, "activity_b1")
        self.wf.start.connect(b1)

        b2 = Activity(self.wf, "activity_b2")
        b1.connect(b2)

        # Merge both branches (synchronized).
        synch_1 = Synchronization(self.wf, "synch_1")
        a2.connect(synch_1)
        b2.connect(synch_1)

        # If-condition that does not match.
        excl_choice_1 = ExclusiveChoice(self.wf, "excl_choice_1")
        synch_1.connect(excl_choice_1)

        c1 = Activity(self.wf, "activity_c1")
        excl_choice_1.connect(c1)

        c2 = Activity(self.wf, "activity_c2")
        excl_choice_1.connect_if(('test_attribute1', ExclusiveChoice.EQUAL, 'test_attribute2'), c2)

        c3 = Activity(self.wf, "activity_c3")
        excl_choice_1.connect_if(('test_attribute1', ExclusiveChoice.EQUAL, 'test_attribute2'), c3)

        # If-condition that matches.
        excl_choice_2 = ExclusiveChoice(self.wf, "excl_choice_2")
        c1.connect(excl_choice_2)
        c2.connect(excl_choice_2)
        c3.connect(excl_choice_2)

        d1 = Activity(self.wf, "activity_d1")
        excl_choice_2.connect(d1)

        d2 = Activity(self.wf, "activity_d2")
        excl_choice_2.connect_if(('test_attribute1', ExclusiveChoice.EQUAL, 'test_attribute2'), d2)

        d3 = Activity(self.wf, "activity_d3")
        excl_choice_2.connect_if(('test_attribute1', ExclusiveChoice.EQUAL, 'test_attribute1'), d3)

        # If-condition that does not match.
        multichoice = MultiChoice(self.wf, "multi_choice_1")
        d1.connect(multichoice)
        d2.connect(multichoice)
        d3.connect(multichoice)

        e1 = Activity(self.wf, "activity_e1")
        multichoice.connect_if(('test_attribute1', ExclusiveChoice.EQUAL, 'test_attribute1'), e1)

        e2 = Activity(self.wf, "activity_e2")
        multichoice.connect_if(('test_attribute1', ExclusiveChoice.EQUAL, 'test_attribute2'), e2)

        e3 = Activity(self.wf, "activity_e3")
        multichoice.connect_if(('test_attribute2', ExclusiveChoice.EQUAL, 'test_attribute2'), e3)

        # StructuredSynchronizingMerge
        syncmerge = StructuredSynchronizingMerge(self.wf, "struct_synch_merge_1", multichoice)
        e1.connect(syncmerge)
        e2.connect(syncmerge)
        e3.connect(syncmerge)

        # Implicit parallel split.
        f1 = Activity(self.wf, "activity_f1")
        syncmerge.connect(f1)

        f2 = Activity(self.wf, "activity_f2")
        syncmerge.connect(f2)

        f3 = Activity(self.wf, "activity_f3")
        syncmerge.connect(f3)

        # StructuredDiscriminator
        discrim_1 = StructuredDiscriminator(self.wf, "struct_discriminator_1", syncmerge)
        f1.connect(discrim_1)
        f2.connect(discrim_1)
        f3.connect(discrim_1)

        # Loop back to the first exclusive choice.
        excl_choice_3 = ExclusiveChoice(self.wf, 'excl_choice_3')
        discrim_1.connect(excl_choice_3)
        excl_choice_3.connect_if(('excl_choice_3_reached', ExclusiveChoice.NOT_EQUAL, 'two'), excl_choice_1)

        # Split into 3 branches, and implicitly split twice in addition.
        multi_instance_1 = MultiInstance(self.wf, 'multi_instance_1', 'three')
        excl_choice_3.connect(multi_instance_1)

        # Parallel activities.
        g1 = Activity(self.wf, "activity_g1")
        g2 = Activity(self.wf, "activity_g2")
        multi_instance_1.connect(g1)
        multi_instance_1.connect(g2)

        # StructuredSynchronizingMerge
        syncmerge2 = StructuredSynchronizingMerge(self.wf, "struct_synch_merge_2", multi_instance_1)
        g1.connect(syncmerge2)
        g2.connect(syncmerge2)

        # Add a final activity.
        last = Activity(self.wf, "last")
        syncmerge2.connect(last)

        last.connect(self.wf.end)
        self.runWorkflow(self.wf)


    def runWorkflow(self, wf):
        for activity in wf.activities:
            activity.user_func = self.print_name

        job = Job(wf)
        job.execute_all()

        path = [(1, 'Start'),
                (1, 'activity_a1'),
                (2, 'activity_b1'),
                (1, 'activity_a2'),
                (2, 'activity_b2'),
                (2, 'synch_1'),
                (2, 'excl_choice_1'),
                (2, 'activity_c1'),
                (2, 'excl_choice_2'),
                (2, 'activity_d3'),
                (2, 'multi_choice_1'),
                (3, 'activity_e1'),
                (4, 'activity_e3'),
                (4, 'struct_synch_merge_1'),
                (4, 'activity_f1'),
                (5, 'activity_f2'),
                (6, 'activity_f3'),
                (4, 'struct_discriminator_1'),
                (4, 'excl_choice_3'),
                (4, 'excl_choice_1'),
                (4, 'activity_c1'),
                (4, 'excl_choice_2'),
                (4, 'activity_d3'),
                (4, 'multi_choice_1'),
                (7, 'activity_e1'),
                (8, 'activity_e3'),
                (8, 'struct_synch_merge_1'),
                (8, 'activity_f1'),
                (9, 'activity_f2'),
                (10, 'activity_f3'),
                (8, 'struct_discriminator_1'),
                (8, 'excl_choice_3'),
                (8, 'multi_instance_1'),
                (11, 'activity_g1'),
                (12, 'activity_g2'),
                (13, 'activity_g1'),
                (14, 'activity_g2'),
                (15, 'activity_g1'),
                (16, 'activity_g2'),
                (16, 'struct_synch_merge_2'),
                (16, 'last')]

        # Check whether the correct route was taken.
        for i, (branch, name) in enumerate(path):
            self.assert_(i < len(self.path),
                         'Taken route is too short: %s' % self.path)
            self.assert_(name == self.path[i][1],
                         'Incorrect route taken at step %s (%s):\n%s' % (i + 1, self.path[i][1], self.format_path(self.path)))
        self.assert_(len(self.path) == len(path),
                     'Taken route is too long: %s' % self.path)

        # Check whether all activities were in the correct branch.
        for i, (branch, name) in enumerate(path):
            self.assert_(branch == self.path[i][0],
                         'Step %s (%s) in incorrect branch:\n%s' % (i + 1, self.path[i][1], self.format_path(self.path)))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())

#import pickle
#output = open('data.pkl', 'wb')
#pickle.dump(one, output)
#output.close()
