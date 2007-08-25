import sys, unittest
sys.path.insert(0, '..')

def suite():
    tests = ['testWorkflow']
    return unittest.TestSuite(map(WorkflowTest, tests))

from Activities import *
from Workflow   import Workflow
from Job        import Job

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
    taken_path  = job.get_attribute('taken_path', [])
    split_point = branch_node.get_branch_start()
    root_id     = branch_node._get_root().id
    id          = split_point.id - root_id + 1
    taken_path.append((id, activity.name))
    job.set_attribute(taken_path = taken_path)
    #print "%s. Branch '%s': %s reached %s times" % (step, id, activity.name, n_reached)

class WorkflowTest(unittest.TestCase):
    """
    WARNING: Make sure to keep this test in sync with XmlReaderTest! Any
    change will break both tests!
    """
    def setUp(self):
        self.wf            = Workflow()
        self.expected_path = [( 1, 'Start'),
                              ( 3, 'activity_a1'),
                              ( 3, 'activity_a2'),
                              ( 4, 'activity_b1'),
                              ( 4, 'activity_b2'),
                              ( 4, 'synch_1'),
                              ( 4, 'excl_choice_1'),
                              ( 4, 'activity_c1'),
                              ( 4, 'excl_choice_2'),
                              ( 4, 'activity_d3'),
                              ( 4, 'multi_choice_1'),
                              (14, 'activity_e1'),
                              (15, 'activity_e3'),
                              (15, 'struct_synch_merge_1'),
                              (18, 'activity_f1'),
                              (18, 'struct_discriminator_1'),
                              (18, 'excl_choice_3'),
                              (18, 'excl_choice_1'),
                              (18, 'activity_c1'),
                              (18, 'excl_choice_2'),
                              (18, 'activity_d3'),
                              (18, 'multi_choice_1'),
                              (28, 'activity_e1'),
                              (29, 'activity_e3'),
                              (29, 'struct_synch_merge_1'),
                              (32, 'activity_f1'),
                              (32, 'struct_discriminator_1'),
                              (32, 'excl_choice_3'),
                              (32, 'multi_instance_1'),
                              (33, 'activity_f2'),
                              (38, 'activity_g1'),
                              (39, 'activity_g2'),
                              (40, 'activity_g1'),
                              (41, 'activity_g2'),
                              (42, 'activity_g1'),
                              (43, 'activity_g2'),
                              (43, 'struct_synch_merge_2'),
                              (43, 'last'),
                              (43, 'End'),
                              (34, 'activity_f3'),
                              (19, 'activity_f2'),
                              (20, 'activity_f3')]


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
        syncmerge = Synchronization(self.wf, "struct_synch_merge_1", multichoice)
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

        # Discriminator
        discrim_1 = Discriminator(self.wf, "struct_discriminator_1", syncmerge)
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
        syncmerge2 = Synchronization(self.wf, "struct_synch_merge_2", multi_instance_1)
        g1.connect(syncmerge2)
        g2.connect(syncmerge2)

        # Add a final activity.
        last = Activity(self.wf, "last")
        syncmerge2.connect(last)

        last.connect(self.wf.end)
        self.runWorkflow(self.wf)


    def runWorkflow(self, wf):
        for activity in wf.activities:
            activity.user_func = print_name

        # Execute all activities within the Job.
        job = Job(wf)
        job.execute_all()

        #job.branch_tree.dump()

        # Check whether the correct route was taken.
        taken_path = job.get_attribute('taken_path', [])
        for i, (branch, name) in enumerate(self.expected_path):
            self.assert_(i < len(taken_path),
                         'Taken route is too short: %s' % taken_path)
            self.assert_(name == taken_path[i][1],
                         'Incorrect route taken at step %s (%s):\n%s' % (i + 1, taken_path[i][1], self.format_path(taken_path)))
        self.assert_(len(taken_path) == len(self.expected_path),
                     'Taken route is too long: %s' % taken_path)

        # Check whether all activities were in the correct branch.
        for i, (branch, name) in enumerate(self.expected_path):
            self.assert_(branch == taken_path[i][0],
                         'Step %s (%s) in incorrect branch:\n%s' % (i + 1, taken_path[i][1], self.format_path(taken_path)))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
