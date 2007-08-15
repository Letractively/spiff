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
class Branch(object):
    """
    This class implements a branch (= a taken path) within the workflow.
    """

    def __init__(self, id, job, first_activity):
        """
        Constructor.
        """
        assert id             is not None
        assert job            is not None
        assert first_activity is not None
        self.id           = id
        self.job          = job
        self.path         = [first_activity.id] # The path of taken/next activities.
        self.activity_map = {first_activity.id: first_activity}
        self.current      = 0


    def copy(self, id):
        """
        Returns a copy of this branch.

        id -- the id of the new copy
        """
        first               = self.activity_map[self.path[0]]
        branch              = Branch(id, self.job, first)
        branch.path         = self.path[:]
        branch.activity_map = self.activity_map.copy()
        branch.current      = self.current
        return branch


    def clear_queue(self):
        """
        Removes all future activities from the path.
        """
        self.path = self.path[:self.current + 1]


    def get_path(self, start = None, end = None):
        """
        Returns a copy of the path, beginning from the first occurence
        of the given start activity, and ending at the LAST occurence
        of the given end activity.

        start -- the activity at which the path begins. If None is given,
                 the path starts at the first activity.
        end -- the activity at which the path ends. If None is given,
               the complete path is returned.
        """
        # Find the beginning of the path.
        start_pos = 0
        if start is not None:
            start_pos = self.path.index(start.id)

        # Find the end of the path.
        if end is not None:
            end_pos = 0
            for i in xrange(len(self.path) - 1, -1, -1):
                if self.path[i] == end.id:
                    end_pos = i
                    break
            return '/'.join(['%s' % id for id in self.path[start_pos:end_pos]])

        return '/'.join(['%s' % id for id in self.path[start_pos:]])


    def queue_next_activity(self, activity):
        """
        Called by an activity to enqueue its successor in the workflow to the
        branch.
        """
        assert activity is not None
        self.path.append(activity.id)
        self.activity_map[activity.id] = activity


    def activity_completed_notify(self, activity):
        """
        Called by an activity when it is completed.
        """
        assert activity.id == self.path[self.current]
        self.current += 1
        next_activity = self.activity_map[self.path[self.current]]
        next_activity.completed_notify(self.job, self, activity)


    def execute_next(self):
        """
        Executes the next activity in the branch (if it is ready to run).
        Returns True if the activity was executed, False otherwise.
        """
        assert self.id >= 0
        next_activity = self.activity_map[self.path[self.current]]
        if len(next_activity.outputs) == 0:
            self.job.branch_completed_notify(self)
            return False
        return next_activity.execute(self.job, self)
