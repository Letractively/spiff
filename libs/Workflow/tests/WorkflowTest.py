import sys, unittest
sys.path.insert(0, '..')

def suite():
    tests = ['testWorkflow']
    return unittest.TestSuite(map(WorkflowTest, tests))

from Tasks import *
from Workflow   import Workflow
from Job        import Job

def print_name(branch_node, task):
    job         = branch_node.job
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
    taken_path  = job.get_attribute('taken_path', [])
    id          = branch_node.thread_id
    taken_path.append((id, task.name))
    job.set_attribute(taken_path = taken_path)
    #print "%s. Branch '%s': %s reached %s times" % (step, id, task.name, n_reached)
    return True

class WorkflowTest(unittest.TestCase):
    """
    WARNING: Make sure to keep this test in sync with XmlReaderTest! Any
    change will break both tests!
    """
    def setUp(self):
        self.wf            = Workflow()
        self.expected_path = [( 1, 'Start'),
                              ( 3, 'task_a1'),
                              ( 3, 'task_a2'),
                              ( 4, 'task_b1'),
                              ( 4, 'task_b2'),
                              ( 4, 'synch_1'),
                              ( 4, 'excl_choice_1'),
                              ( 4, 'task_c1'),
                              ( 4, 'excl_choice_2'),
                              ( 4, 'task_d3'),
                              ( 4, 'multi_choice_1'),
                              (14, 'task_e1'),
                              (15, 'task_e3'),
                              (15, 'struct_synch_merge_1'),
                              (18, 'task_f1'),
                              (18, 'struct_discriminator_1'),
                              (18, 'excl_choice_3'),
                              (18, 'excl_choice_1'),
                              (18, 'task_c1'),
                              (18, 'excl_choice_2'),
                              (18, 'task_d3'),
                              (18, 'multi_choice_1'),
                              (28, 'task_e1'),
                              (29, 'task_e3'),
                              (29, 'struct_synch_merge_1'),
                              (32, 'task_f1'),
                              (32, 'struct_discriminator_1'),
                              (32, 'excl_choice_3'),
                              (32, 'multi_instance_1'),
                              (38, 'task_g1'),
                              (39, 'task_g2'),
                              (40, 'task_g1'),
                              (41, 'task_g2'),
                              (42, 'task_g1'),
                              (43, 'task_g2'),
                              (43, 'struct_synch_merge_2'),
                              (43, 'last'),
                              (43, 'End'),
                              (33, 'task_f2'),
                              (34, 'task_f3'),
                              (19, 'task_f2'),
                              (20, 'task_f3')]


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
        a1 = Task(self.wf, "task_a1")
        self.wf.start.connect(a1)

        a2 = Task(self.wf, "task_a2")
        a1.connect(a2)

        # Build another branch.
        b1 = Task(self.wf, "task_b1")
        self.wf.start.connect(b1)

        b2 = Task(self.wf, "task_b2")
        b1.connect(b2)

        # Merge both branches (synchronized).
        synch_1 = Join(self.wf, "synch_1")
        a2.connect(synch_1)
        b2.connect(synch_1)

        # If-condition that does not match.
        excl_choice_1 = ExclusiveChoice(self.wf, "excl_choice_1")
        synch_1.connect(excl_choice_1)

        c1 = Task(self.wf, "task_c1")
        excl_choice_1.connect(c1)

        c2 = Task(self.wf, "task_c2")
        cond = Condition(Condition.EQUAL,
                         left_attribute  = 'test_attribute1',
                         right_attribute = 'test_attribute2')
        excl_choice_1.connect_if(cond, c2)

        c3 = Task(self.wf, "task_c3")
        excl_choice_1.connect_if(cond, c3)

        # If-condition that matches.
        excl_choice_2 = ExclusiveChoice(self.wf, "excl_choice_2")
        c1.connect(excl_choice_2)
        c2.connect(excl_choice_2)
        c3.connect(excl_choice_2)

        d1 = Task(self.wf, "task_d1")
        excl_choice_2.connect(d1)

        d2 = Task(self.wf, "task_d2")
        excl_choice_2.connect_if(cond, d2)

        d3 = Task(self.wf, "task_d3")
        cond = Condition(Condition.EQUAL,
                         left_attribute  = 'test_attribute1',
                         right_attribute = 'test_attribute1')
        excl_choice_2.connect_if(cond, d3)

        # If-condition that does not match.
        multichoice = MultiChoice(self.wf, "multi_choice_1")
        d1.connect(multichoice)
        d2.connect(multichoice)
        d3.connect(multichoice)

        e1 = Task(self.wf, "task_e1")
        multichoice.connect_if(cond, e1)

        e2 = Task(self.wf, "task_e2")
        cond = Condition(Condition.EQUAL,
                         left_attribute  = 'test_attribute1',
                         right_attribute = 'test_attribute2')
        multichoice.connect_if(cond, e2)

        e3 = Task(self.wf, "task_e3")
        cond = Condition(Condition.EQUAL,
                         left_attribute  = 'test_attribute2',
                         right_attribute = 'test_attribute2')
        multichoice.connect_if(cond, e3)

        # StructuredSynchronizingMerge
        syncmerge = Join(self.wf, "struct_synch_merge_1", 'multi_choice_1')
        e1.connect(syncmerge)
        e2.connect(syncmerge)
        e3.connect(syncmerge)

        # Implicit parallel split.
        f1 = Task(self.wf, "task_f1")
        syncmerge.connect(f1)

        f2 = Task(self.wf, "task_f2")
        syncmerge.connect(f2)

        f3 = Task(self.wf, "task_f3")
        syncmerge.connect(f3)

        # Discriminator
        discrim_1 = Join(self.wf,
                         "struct_discriminator_1",
                         'struct_synch_merge_1',
                         threshold = 1)
        f1.connect(discrim_1)
        f2.connect(discrim_1)
        f3.connect(discrim_1)

        # Loop back to the first exclusive choice.
        excl_choice_3 = ExclusiveChoice(self.wf, 'excl_choice_3')
        discrim_1.connect(excl_choice_3)
        cond = Condition(Condition.NOT_EQUAL,
                         left_attribute  = 'excl_choice_3_reached',
                         right_attribute = 'two')
        excl_choice_3.connect_if(cond, excl_choice_1)

        # Split into 3 branches, and implicitly split twice in addition.
        multi_instance_1 = MultiInstance(self.wf, 'multi_instance_1', times = 3)
        excl_choice_3.connect(multi_instance_1)

        # Parallel tasks.
        g1 = Task(self.wf, "task_g1")
        g2 = Task(self.wf, "task_g2")
        multi_instance_1.connect(g1)
        multi_instance_1.connect(g2)

        # StructuredSynchronizingMerge
        syncmerge2 = Join(self.wf, "struct_synch_merge_2", 'multi_instance_1')
        g1.connect(syncmerge2)
        g2.connect(syncmerge2)

        # Add a final task.
        last = Task(self.wf, "last")
        syncmerge2.connect(last)

        # Add another final task :-).
        end = Task(self.wf, "End")
        last.connect(end)

        self.runWorkflow(self.wf)


    def runWorkflow(self, wf):
        for name in wf.tasks:
            wf.tasks[name].user_func = print_name

        # Execute all tasks within the Job.
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

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
