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
from Form        import Form
from StockButton import StockButton

class CollectDBInfo(Task):
    __db_config = {
      'mysql3': {
        'hostname': 'Database Server:',
        'db_name':  'Database Name:',
        'user':     'Username:',
        'password': 'Password:'
      },
      'mysql4': {
        'hostname': 'Database Server:',
        'db_name':  'Database Name:',
        'user':     'Username:',
        'password': 'Password:'
      },
      'sqlite': { }
    }

    def __init__(self, supported_db_types = None):
        Task.__init__(self, 'Please enter your database information')
        # Make sure that the argument list makes sense.
        if supported_db_types is not None:
            for type in supported_db_types:
                if type not in self.__db_config.keys():
                    assert False # Database type not supported

        # Create a list of all supported databases.
        self.__supported_db_types = {}
        for db_type in self.__db_config.keys():
            if supported_db_types is None or db_type in supported_db_types:
                self.__supported_db_types[db_type] = self.__db_config[db_type]


    def install(self, environment):
        result = environment.get_interaction_result()
        if not result:
            # Generate a form for selecting the database.
            markup  = '{title "Please select your database type."}'
            markup += '{variable db_type_sent "True"}'
            markup += '{label "Database Type:"} {select db_type}'
            for db_type in self.__supported_db_types.keys():
                markup += '  {item %s}' % db_type
            markup += '{end_select}'
            form = Form(markup, [StockButton('next_button')])
            environment.render_markup(form)
            return Task.interact

        elif result.get('db_type_sent') is not None:
            # Show a form for entering the database details.
            db_type = result.get('db_type')
            assert self.__supported_db_types.has_key(db_type)
            markup  = '{title "Please enter your database details."}'
            markup += '{variable db_details_sent "True"}'
            markup += '{variable db_type "%s"}' % db_type
            for key in self.__supported_db_types[db_type]:
                caption = self.__supported_db_types[db_type][key]
                markup += '{label "%s"} {entry %s}\n' % (caption, key)
            form = Form(markup, [StockButton('next_button')])
            environment.render_markup(form)
            return Task.interact

        elif result.get('db_details_sent') is not None:
            # Store the data in the environment so other tasks can access it.
            db_type    = result.get('db_type')
            db_details = {'db_type': db_type}
            for key in self.__supported_db_types[db_type]:
                db_details[key] = result.get(key)
            environment.set_attribute('db_details', db_details)

        else:
            assert False # Invalid response

        return Task.success


    def uninstall(self, environment):
        return Task.success


if __name__ == '__main__':
    import unittest
    import cgi
    from WebEnvironment import WebEnvironment

    class CollectDBInfoTest(unittest.TestCase):
        def runTest(self):
            environment = WebEnvironment(cgi.FieldStorage())
            task        = CollectDBInfo()
            assert task.install(environment)   == Task.interact
            assert task.uninstall(environment) == Task.success

    testcase = CollectDBInfoTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
