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
from Actor import *

class ActorGroup(Actor):
    def __init__(self, name, handle = None):
        Actor.__init__(self, name, handle)
        self.remove_attribute('auth_hash')

    def is_group(self):
        return True

    def set_auth_string(self, auth_string):
        pass

    def has_auth_string(self, auth_string):
        return False


if __name__ == '__main__':
    import unittest

    class ActorGroupTest(unittest.TestCase):
        def runTest(self):
            name   = 'Test ActorGroup'
            actor_group = ActorGroup(name)
            assert actor_group.get_id()     == -1
            assert actor_group.get_name()   == name
            assert actor_group.get_handle() == make_handle_from_string(name)
            assert actor_group.is_group()   == True
            
            pwd = 'Testpwd'
            actor_group.set_auth_string(pwd)
            assert actor_group.has_auth_string(pwd)         == False
            assert actor_group.has_auth_string('incorrect') == False

    testcase = ActorGroupTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
