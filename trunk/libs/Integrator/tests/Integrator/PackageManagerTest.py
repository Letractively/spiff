import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'Integrator'))

def suite():
    tests = ['testManager']
    return unittest.TestSuite(map(PackageManagerTest, tests))

from DBTest         import DBTest
from Api            import Api
from PackageManager import PackageManager

class PackageManagerTest(DBTest):
    def setUp(self):
        DBTest.setUp(self)
        api          = Api()
        self.manager = PackageManager(self.guard, api)
        self.manager.set_package_dir('tmp')
        
    def testManager(self):
        self.assertRaises(IOError, self.manager.read_package, 'no_such_file')
        self.assertRaises(IOError, self.manager.set_package_dir, 'dir')

        # Install first package.
        filename = '../samples/SpiffExtension'
        pkg1     = self.manager.read_package(filename)
        self.manager.install_package(pkg1)
        self.assert_(pkg1.get_id() is not None)

        # Install second package.
        filename = '../samples/HelloWorldExtension'
        pkg2     = self.manager.read_package(filename)
        self.manager.install_package(pkg2)
        self.assert_(pkg2.get_id() is not None)

        # Remove the package.
        self.manager.remove_package(pkg2)
        self.manager.remove_package_from_id(pkg1.get_id())

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
