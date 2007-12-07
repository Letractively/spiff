import sys, unittest, re
sys.path.insert(0, '..')
sys.path.insert(0, '../..')

def suite():
    tests = ['testManager']
    return unittest.TestSuite(map(ManagerTest, tests))

from DBTest         import DBTest
from Api            import Api
from PackageManager import PackageManager

class ManagerTest(DBTest):
    def setUp(self):
        DBTest.setUp(self)
        api          = Api()
        self.manager = PackageManager(self.guard, api)
        self.manager.set_package_dir('tmp')
        
    def testManager(self):
        self.assertRaises(IOError, self.manager.add_package, 'no_such_file')
        self.assertRaises(IOError, self.manager.set_package_dir, 'dir')

        # Install first package.
        filename = '../samples/SpiffExtension'
        pkg1     = self.manager.add_package(filename)
        self.assert_(pkg1.get_id() is not None)

        # Install second package.
        filename = '../samples/HelloWorldExtension'
        pkg2     = self.manager.add_package(filename)
        self.assert_(pkg2.get_id() is not None)

        # Remove the package.
        self.manager.remove_package(pkg2)
        self.manager.remove_package_from_id(pkg1.get_id())

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
