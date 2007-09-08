import sys, unittest, re
sys.path.insert(0, '..')
sys.path.insert(0, '../..')

def suite():
    tests = ['testManager']
    return unittest.TestSuite(map(ManagerTest, tests))

from DBTest  import DBTest
from Api     import Api
from Manager import Manager

class ManagerTest(DBTest):
    def setUp(self):
        DBTest.setUp(self)
        api          = Api()
        self.manager = Manager(self.guard, api)
        self.manager.set_extension_dir('tmp')
        
    def testManager(self):
        self.assertRaises(IOError, self.manager.add_extension, 'no_such_file')
        self.assertRaises(IOError, self.manager.set_extension_dir, 'dir')

        # Install first extension.
        filename = '../samples/SpiffExtension'
        id1      = self.manager.add_extension(filename)
        self.assert_(id1 > 0, "Id is %s" % id1)

        # Install second extension.
        filename = '../samples/HelloWorldExtension'
        id2      = self.manager.add_extension(filename)
        self.assert_(id2 > 0, "Id is %s" % id2)

        # Remove the extension.
        self.assert_(self.manager.remove_extension_from_id(id2))
        self.assert_(self.manager.remove_extension_from_id(id1))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
