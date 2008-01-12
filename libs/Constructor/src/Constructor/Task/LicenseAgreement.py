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
from Task   import Task
from Form   import Form
from Button import Button

class LicenseAgreement(Task):
    def __init__(self, license_text):
        assert license_text is not None
        Task.__init__(self, 'License Agreement')
        self.__license_text = license_text


    def install(self, environment):
        result = environment.get_interaction_result()
        if not result:
            buttons = [Button('agree_button', 'I Agree To The Above License')]
            form    = Form(self.__license_text, buttons)
            environment.render_markup(form)
            return Task.interact
        return Task.success


    def uninstall(self, environment):
        return Task.success


if __name__ == '__main__':
    import unittest
    import cgi
    from WebEnvironment import WebEnvironment

    class LicenseAgreementTest(unittest.TestCase):
        def runTest(self):
            environment = WebEnvironment(cgi.FieldStorage())
            license     = 'Give me your soul'
            task        = LicenseAgreement(license)
            assert task.install(environment)   == Task.interact
            assert task.uninstall(environment) == Task.success

    testcase = LicenseAgreementTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)

