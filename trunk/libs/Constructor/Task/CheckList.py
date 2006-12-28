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
from Task        import Task
from Group       import Group
from Form        import Form
from StockButton import StockButton

class CheckList(Group):
    def __init__(self, name = None, child_task = []):
        assert child_task is not None
        if name is None:
            name = 'Checklist'
        Group.__init__(self, name, child_task)


    def get(self, n):
        return None


    def install(self, environment):
        result = environment.get_interaction_result()
        if result is not None and result.get('check_done') is not None:
            return Task.success
        result  = Task.success
        markup  = '{title "%s"}' % self._name
        for task in self._child_task:
            result = task.install(environment)
            label  = task.get_name()
            if result is not Task.success:
                markup += '{label "%s:"} {label "%s"}\n' % (label, 'Failed')
                break
            markup += '{label "%s:"} {label "%s"}\n' % (label, 'Success')
        if result == Task.success:
            markup += '{variable check_done "True"}'
            form = Form(markup, [StockButton('next_button')])
        else:
            form = Form(markup, [StockButton('retry_button')])
        environment.render_markup(form)
        return Task.interact


    def uninstall(self, environment):
        return Task.success


if __name__ == '__main__':
    import unittest
    import cgi
    from WebEnvironment import WebEnvironment
    from ExecCommand    import ExecCommand

    class CheckListTest(unittest.TestCase):
        def runTest(self):
            environment = WebEnvironment(cgi.FieldStorage())
            task1       = ExecCommand('Subtask 1', 'True',  'True')
            task2       = ExecCommand('Subtask 2', 'False', 'False')
            gname       = 'Test Task CheckList'
            checklist   = CheckList(gname, [task1, task2])
            assert checklist.get_name()             == gname
            assert task1.install(environment)       == Task.success
            assert task2.install(environment)       == Task.failure
            assert task1.uninstall(environment)     == Task.success
            assert task2.uninstall(environment)     == Task.failure
            assert checklist.install(environment)   == Task.interact
            assert checklist.uninstall(environment) == Task.success

    testcase = CheckListTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)