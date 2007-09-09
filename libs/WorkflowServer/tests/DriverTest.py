import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testInstall', 'testDriver']
    return unittest.TestSuite(map(DriverTest, tests))

from DBTest       import DBTest
from Driver       import Driver
from Exceptions   import WorkflowServerException
from WorkflowInfo import WorkflowInfo
from TaskInfo     import TaskInfo

class DriverTest(DBTest):
    def setUp(self):
        self.connectDB()
        self.driver = Driver(self.engine)


    def testInstall(self):
        self.assert_(self.driver.uninstall())
        self.assert_(self.driver.install())
        self.assert_(self.driver.uninstall())
        self.assert_(self.driver.install())


    def testDriver(self):
        self.assert_(self.driver is not None)

        # Create a workflow.
        workflow_info = WorkflowInfo('my/workflow', file = 'parallel_split.xml')
        self.assertRaises(WorkflowServerException,
                          self.driver.create_job,
                          workflow_info)
        self.driver.save_workflow_info(workflow_info)
        self.assert_(workflow_info.id >= 0)

        # Instantiate the workflow.
        job_info = self.driver.create_job(workflow_info)
        self.assert_(job_info.id >= 0)

        # Retrieve a list of tasks.
        task_info_list = self.driver.get_task_info(job_id = job_info.id)
        self.assert_(len(task_info_list) == 10)
        task_info_list = self.driver.get_task_info(job_id = job_info.id,
                                                   status = TaskInfo.WAITING)
        self.assert_(len(task_info_list) == 1)

        # Execute a few tasks.
        self.driver.execute_task(task_info_list[0])
        task_info_list = self.driver.get_task_info(job_id = job_info.id,
                                                   status = TaskInfo.WAITING)
        self.assert_(len(task_info_list) == 1)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
