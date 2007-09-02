# Copyright (C) 2007 Samuel Abels
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
import os.path
from BranchNode import *
from Exception  import WorkflowException
from Task       import Task
from Storage    import XmlReader
from Job        import Job

class SubWorkflow(Task):
    """
    A SubWorkflow is a task that wraps a Workflow, such that you can re-use it
    in multiple places as if it were a task.
    If more than one input is connected, the task performs an implicit
    multi merge.
    If more than one output is connected, the task performs an implicit
    parallel split.
    """

    def __init__(self, parent, name, **kwargs):
        """
        Constructor.

        parent -- a reference to the parent (Task)
        name -- a name for the task (string)
        kwargs -- may contain the following keys:
                  file -- name of a file containing a workflow
                  file_attribute -- name of an attribute that contains
                  the name of a workflow file
        """
        assert parent  is not None
        assert name    is not None
        assert kwargs.has_key('file') or kwargs.has_key('file_attribute')
        Task.__init__(self, parent, name, **kwargs)
        self.file           = None
        self.file_attribute = kwargs.get('file_attribute', None)
        self.in_assign      = kwargs.get('in_assign',      [])
        self.out_assign     = kwargs.get('out_assign',     [])
        if kwargs.has_key('file'):
            dirname   = os.path.dirname(parent.file)
            self.file = os.path.join(dirname, kwargs['file'])


    def test(self):
        Task.test(self)
        if self.file is not None and not os.path.exists(self.file):
            raise WorkflowException(self, 'File does not exist: %s' % self.file)


    def _on_subjob_completed(self, subjob, branch_node):
        # Assign variables, if so requested.
        for assignment in self.out_assign:
            assignment.assign(subjob, branch_node.job)
        for output in self.outputs:
            branch_node.add_child(output)


    def _execute(self, job, branch_node):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.

        job -- the job in which this method is executed
        branch_node -- the branch_node in which this method is executed
        """
        file = self.file
        if file is None:
            file = job.get_attribute(self.file_attribute)
        xml_reader    = XmlReader()
        workflow_list = xml_reader.parse_file(self.file)
        workflow      = workflow_list[0]
        subjob        = Job(workflow,
                            on_complete      = self._on_subjob_completed,
                            on_complete_data = branch_node)
        # Assign variables, if so requested.
        for assignment in self.in_assign:
            assignment.assign(branch_node.job, subjob)
        branch_node.children = subjob.branch_tree.children
        return True
