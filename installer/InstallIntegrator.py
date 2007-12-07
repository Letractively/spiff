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
from Integrator import PackageManager, Api
from sqlalchemy import *

class InstallIntegrator(Task):
    def __init__(self):
        Task.__init__(self, 'Installing Spiff Integrator')


    def install(self, environment):
        guard = environment.get_attribute('guard_db')
        assert guard is not None
        integrator = PackageManager(guard, Api())
        integrator.install()
        environment.set_attribute('integrator_db', integrator)
        return Task.success


    def uninstall(self, environment):
        guard = environment.get_attribute('guard_db')
        assert guard is not None
        integrator = Integrator.DB(guard)
        integrator.uninstall()
        return Task.success


if __name__ == '__main__':
    import unittest
    import cgi
    from ConfigParser import RawConfigParser
    from WebEnvironment import WebEnvironment

    class InstallIntegratorTest(unittest.TestCase):
        def runTest(self):
            environment = WebEnvironment(cgi.FieldStorage())
            task        = InstallIntegrator()
            assert task.install(environment)   == Task.success
            assert task.uninstall(environment) == Task.success

    testcase = InstallIntegratorTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
