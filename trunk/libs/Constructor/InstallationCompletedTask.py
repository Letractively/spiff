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
from Task import Task
from Form import Form

class InstallationCompletedTask(Task):
    def __init__(self, text = None):
        Task.__init__(self, 'Installation completed.')
        if text is None:
            self.__text = 'Your installation is now complete!'
        else:
            self.__text = text


    def install(self, environment):
        form = Form(self.__text, [])
        environment.show_form(form)
        return Task.success


    def uninstall(self, environment):
        return True


if __name__ == '__main__':
    import unittest
    import cgi
    from WebEnvironment import WebEnvironment

    class InstallationCompletedTaskTest(unittest.TestCase):
        def runTest(self):
            environment = WebEnvironment(cgi.FieldStorage())
            license     = 'Give me your soul'
            task        = InstallationCompletedTask(license)
            assert task.install(environment)   == Task.success
            assert task.uninstall(environment) == True

    testcase = InstallationCompletedTaskTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
