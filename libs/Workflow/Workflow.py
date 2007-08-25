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
from Activities import StartActivity
from Activities import StubActivity

class Workflow(object):
    """
    This class represents an entire workflow.
    """

    def __init__(self, name = ''):
        """
        Constructor.
        """
        self.name       = name
        self.activities = []
        self.start      = StartActivity(self)


    def add_notify(self, activity):
        """
        Called by an activity when it was added into the workflow.
        """
        self.activities.append(activity)
        activity.id = len(self.activities)
