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
from Task       import Task
from sqlalchemy import *
from User       import User
from Group      import Group
from Page       import Page
from UserAction import UserAction
from PageAction import PageAction
import Guard

class InstallGuard(Task):
    def __init__(self):
        Task.__init__(self, 'Installing Spiff Guard')


    def install(self, environment):
        dbn = environment.get_attribute('dbn')
        assert dbn is not None
        engine = create_engine(dbn)
        guard  = Guard.DB(engine)
        try:
            guard.install()
            guard.register_type([User,
                                 Group,
                                 Page,
                                 UserAction,
                                 PageAction])
        except Exception, e:
            print "FAIL:", e
            return Task.failure
        environment.set_attribute('guard_db', guard)
        return Task.success


    def uninstall(self, environment):
        dbn = environment.get_attribute('dbn')
        assert dbn is not None
        engine = create_engine(dbn)
        guard  = Guard.DB(engine)
        try:
            guard.uninstall()
        except:
            pass
        return Task.success


if __name__ == '__main__':
    import unittest
    import cgi
    from ConfigParser import RawConfigParser
    from WebEnvironment import WebEnvironment

    class InstallGuardTest(unittest.TestCase):
        def runTest(self):
            environment = WebEnvironment(cgi.FieldStorage())
            task        = InstallGuard()
            assert task.install(environment)   == Task.success
            assert task.uninstall(environment) == Task.success

    testcase = InstallGuardTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
