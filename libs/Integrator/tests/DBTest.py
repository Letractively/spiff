import sys, unittest, re
sys.path.insert(0, '..')
sys.path.insert(0, '../..')

def suite():
    tests = ['testSetTablePrefix',
             'testCheckDependencies',
             'testRegisterExtension',
             'testUnregisterExtension',
             'testGetExtension',
             'testCallback']
    return unittest.TestSuite(map(DBTest, tests))

import MySQLdb
import Guard
from sqlalchemy     import create_engine
from sqlalchemy.orm import clear_mappers
from ConfigParser   import RawConfigParser
from DB             import DB
from ExtensionInfo  import ExtensionInfo

def dummy_callback(args):
    pass

class DBTest(unittest.TestCase):
    def setUp(self):
        # Read config.
        cfg = RawConfigParser()
        cfg.read('unit_test.cfg')
        host     = cfg.get('database', 'host')
        db_name  = cfg.get('database', 'db_name')
        user     = cfg.get('database', 'user')
        password = cfg.get('database', 'password')

        # Connect to MySQL.
        auth        = user + ':' + password
        dbn         = 'mysql://' + auth + '@' + host + '/' + db_name
        self.engine = create_engine(dbn)
        clear_mappers()
        self.guard  = Guard.DB(self.engine)
        self.extdb  = DB(self.guard)

        # Install.
        self.assert_(self.extdb.uninstall())
        self.assert_(self.guard.uninstall())
        self.assert_(self.guard.install())
        self.assert_(self.extdb.install())


    def tearDown(self):
        self.assert_(self.extdb.clear_database())
        self.assert_(self.extdb.uninstall())
        self.assert_(self.guard.uninstall())


    def testSetTablePrefix(self):
        self.assert_(self.extdb.clear_database())
        self.assert_(self.extdb.get_table_prefix() == 'integrator_')
        self.extdb.set_table_prefix('test')
        self.assert_(self.extdb.get_table_prefix() == 'test')
        self.extdb.set_table_prefix('integrator_')
        self.assert_(self.extdb.get_table_prefix() == 'integrator_')


    def testCheckDependencies(self):
        self.assert_(self.extdb.clear_database())
        extension = ExtensionInfo('Spiff')
        extension.set_version('0.2')
        self.extdb.register_extension(extension)
        
        extension = ExtensionInfo('Depends on Spiff')
        self.assert_(self.extdb.check_dependencies(extension))
        extension.add_dependency('spiff>=0.1')
        self.assert_(self.extdb.check_dependencies(extension))
        extension.add_dependency('spiff=0.2')
        self.assert_(self.extdb.check_dependencies(extension))
        extension.add_dependency('spuff>=0.1')
        self.assert_(not self.extdb.check_dependencies(extension))
        extension.add_dependency('spiff>=0.3')
        self.assert_(not self.extdb.check_dependencies(extension))


    def testRegisterExtension(self):
        self.assert_(self.extdb.clear_database())
        extension = ExtensionInfo('Spiff')
        extension.set_version('0.2')
        self.extdb.register_extension(extension)


    def testUnregisterExtension(self):
        self.assert_(self.extdb.clear_database())
        extension = ExtensionInfo('Spiff')
        extension.set_version('0.1.2')
        self.extdb.register_extension(extension)
        self.assert_(self.extdb.unregister_extension_from_id(extension.get_id()))

        extension = ExtensionInfo('Spiff')
        extension.set_version('0.1.2')
        self.extdb.register_extension(extension)
        self.assert_(self.extdb.unregister_extension_from_handle(extension.get_handle(),
                                                   extension.get_version()))
        
        extension = ExtensionInfo('Spiff')
        extension.set_version('0.1.2')
        self.extdb.register_extension(extension)
        self.assert_(self.extdb.unregister_extension(extension))
        
        
    def testGetExtension(self):
        self.assert_(self.extdb.clear_database())
        extension = ExtensionInfo('Spiff')
        extension.set_version('0.1')
        self.extdb.register_extension(extension)

        extension = ExtensionInfo('Spiff')
        extension.set_version('0.2')
        extension.add_dependency('spiff=0.1')
        self.extdb.register_extension(extension)

        result = self.extdb.get_extension_from_id(extension.get_id())
        self.assert_(result.get_handle()  == extension.get_handle())
        self.assert_(result.get_version() == extension.get_version())
        self.assert_(len(result.get_dependency_list()) == 1)
        self.assert_(result.get_dependency_list()[0]   == 'spiff=0.1')
        
        result = self.extdb.get_extension_from_handle('spiff', '0.2')
        self.assert_(result.get_id() == extension.get_id())

        result = self.extdb.get_extension_from_descriptor('spiff>=0.1')
        self.assert_(result.get_id()      == extension.get_id())
        self.assert_(result.get_handle()  == extension.get_handle())
        self.assert_(result.get_version() == extension.get_version())

        result = self.extdb.get_extension_from_descriptor('spiff=0.2')
        self.assert_(result.get_id()      == extension.get_id())
        self.assert_(result.get_handle()  == extension.get_handle())
        self.assert_(result.get_version() == extension.get_version())

        list = self.extdb.get_version_list_from_handle('spiff')
        self.assert_(len(list) == 2)
        self.assert_(list[0].get_handle() == 'spiff')
        self.assert_(list[1].get_handle() == 'spiff')


    def testCallback(self):
        self.assert_(self.extdb.clear_database())
        extension = ExtensionInfo('Spiff')
        extension.set_version('0.1.2')
        self.extdb.register_extension(extension)

        #callback = Callback(self.dummy_callback, 'always')
        self.assert_(self.extdb.link_extension_id_to_callback(extension.get_id(),
                                                'always'))

        list = self.extdb.get_extension_id_list_from_callback('always')
        self.assert_(len(list) == 1)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
