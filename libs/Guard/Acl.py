# Copyright (C) 2006 Samuel Abels, http://debain.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
from Action import *

class Acl(object):
    def __init__(self, actor_id, action, resource_id, permit = False):
        self.__actor_id    = int(actor_id)
        self.__action      = action
        self.__resource_id = int(resource_id)
        self.__permit      = bool(permit)

    def set_actor_id(self, actor_id):
        self.__actor_id = int(actor_id)

    def get_actor_id(self):
        return self.__actor_id

    def set_action(self, action):
        self.__action = action

    def get_action(self):
        return self.__action

    def set_resource_id(self, resource_id):
        self.__resource_id = int(resource_id)

    def get_resource_id(self):
        return self.__resource_id

    def set_permit(self, permit):
        self.__permit = bool(permit)

    def get_permit(self):
        return self.__permit


if __name__ == '__main__':
    import unittest

    class AclTest(unittest.TestCase):
        def runTest(self):
            actor_id    = 10
            action      = Action("Test Action")
            resource_id = 12
            permit      = True
            acl = Acl(10, action, resource_id, permit)
            assert acl.get_actor_id()    == actor_id
            assert acl.get_action()      == action
            assert acl.get_resource_id() == resource_id
            assert acl.get_permit()      == permit

    testcase = AclTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
