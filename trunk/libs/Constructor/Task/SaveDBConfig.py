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
import os, os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from sqlalchemy  import *

from Task import Task

class SaveDBConfig(Task):
    def __init__(self, filename):
        assert filename is not None
        Task.__init__(self, 'Writing database configuration')
        self.__filename = filename


    def install(self, environment):
        dbn = environment.get_attribute('dbn')
        assert dbn is not None
        fd = open(self.__filename, 'w')
        try:
            fd.write('[database]\n')
            fd.write('dbn: %s\n' % dbn)
            fd.close()
        except:
            return Task.failure
        return Task.success


    def uninstall(self, environment):
        try:
            os.remove(self.__filename)
        except:
            return Task.failure
        return Task.success


if __name__ == '__main__':
    import unittest
    import cgi
    from ConfigParser import RawConfigParser
    from WebEnvironment import WebEnvironment

    class SaveDBConfigTest(unittest.TestCase):
        def runTest(self):
            # Read db config.
            cfg = RawConfigParser()
            cfg.read('../unit_test.cfg')
            host     = cfg.get('database', 'host')
            db_name  = cfg.get('database', 'db_name')
            user     = cfg.get('database', 'user')
            password = cfg.get('database', 'password')
            auth     = user + ':' + password
            dbn      = 'mysql://' + auth + '@' + host + '/' + db_name

            # Set up task.
            environment = WebEnvironment(cgi.FieldStorage())
            task        = SaveDBConfig('temp_db_config.cfg')
            environment.set_attribute('dbn', dbn)

            # Run.
            assert task.install(environment)   == Task.success
            assert task.uninstall(environment) == Task.success

    testcase = SaveDBConfigTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
