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
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from sqlalchemy  import *

from Task import Task

class CheckDBConnection(Task):
    def __init__(self):
        Task.__init__(self, 'Trying to contact database host')


    def install(self, environment):
        db_details = environment.get_attribute('db_details')
        assert db_details.has_key('db_type')
        assert db_details.has_key('hostname')
        assert db_details.has_key('db_name')
        assert db_details.has_key('user')
        assert db_details.has_key('password')
        if db_details['db_type'] in ['mysql3', 'mysql4']:
            auth    = db_details['user'] + ':' + db_details['password']
            host    = db_details['hostname']
            db_name = db_details['db_name']
            dbn     = 'mysql://%s@%s/%s' % (auth, host, db_name)
            engine  = create_engine(dbn)
            try:
                conn = engine.connect()
            except:
                conn = None
            if conn is not None:
                return Task.success
        return Task.failure


    def uninstall(self, environment):
        return Task.success


if __name__ == '__main__':
    import unittest
    import cgi
    from ConfigParser import RawConfigParser
    from WebEnvironment import WebEnvironment

    class CheckDBConnectionTest(unittest.TestCase):
        def runTest(self):
            # Read db config.
            cfg = RawConfigParser()
            cfg.read('../unit_test.cfg')
            db_details  = {
              'db_type':  'mysql4',
              'hostname': cfg.get('database', 'host'),
              'db_name':  cfg.get('database', 'db_name'),
              'user':     cfg.get('database', 'user'),
              'password': cfg.get('database', 'password')
            }

            # Set up task.
            environment = WebEnvironment(cgi.FieldStorage())
            task        = CheckDBConnection()
            environment.set_attribute('db_details', db_details)

            # Run.
            assert task.install(environment)   == Task.success
            assert task.uninstall(environment) == Task.success

    testcase = CheckDBConnectionTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
