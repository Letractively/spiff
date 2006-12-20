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

class LicenseAgreementTask(Task):
    def __init__(self, license_text):
        assert license_text is not None
        Task.__init__(self, 'License Agreement')
        self.__license_text = license_text


    def install(self, renderer):
        form = Form(self.__license_text, [Form.cancel_button])
        renderer.show_form(form)
        return Task.interact


    def uninstall(self, renderer):
        return True


if __name__ == '__main__':
    import unittest
    from WebRenderer import WebRenderer

    class LicenseAgreementTaskTest(unittest.TestCase):
        def runTest(self):
            renderer = WebRenderer()
            license  = 'Give me your soul'
            task     = LicenseAgreementTask(license)
            assert task.install(renderer)   == Task.interact
            assert task.uninstall(renderer) == True

    testcase = LicenseAgreementTaskTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)

