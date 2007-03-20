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
import os
from Task       import Task
from sqlalchemy import *
import Warehouse

class InstallWarehouse(Task):
    def __init__(self):
        Task.__init__(self, 'Installing Spiff Warehouse')


    def install(self, environment):
        dbn = environment.get_attribute('dbn')
        assert dbn is not None
        engine    = create_engine(dbn)
        warehouse = Warehouse.DB(engine)
        item1     = Warehouse.Item('default')
        file1     = os.path.join(os.path.dirname(__file__), 'homepage.txt')
        item2     = Warehouse.Item('WikiMarkup')
        file2     = os.path.join(os.path.dirname(__file__), 'markup.txt')
        warehouse.set_directory('../data/warehouse')
        item1.set_source_filename(file1)
        item2.set_source_filename(file2)
        try:
            warehouse.install()
            warehouse.add_file(item1)
            warehouse.add_file(item2)
        except:
            return Task.failure
        environment.set_attribute('warehouse_db', warehouse)
        return Task.success


    def uninstall(self, environment):
        dbn = environment.get_attribute('dbn')
        assert dbn is not None
        engine    = create_engine(dbn)
        warehouse = Warehouse.DB(engine)
        try:
            warehouse.uninstall()
        except:
            pass
        return Task.success


if __name__ == '__main__':
    import unittest
    import cgi
    from ConfigParser import RawConfigParser
    from WebEnvironment import WebEnvironment

    class InstallWarehouseTest(unittest.TestCase):
        def runTest(self):
            environment = WebEnvironment(cgi.FieldStorage())
            task        = InstallWarehouse()
            assert task.install(environment)   == Task.success
            assert task.uninstall(environment) == Task.success

    testcase = InstallWarehouseTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
