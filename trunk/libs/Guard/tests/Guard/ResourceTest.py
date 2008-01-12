import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'Guard'))

def suite():
    tests = ['testResource']
    return unittest.TestSuite(map(ResourceTest, tests))

from functions import make_handle_from_string
from Resource  import Resource

class ResourceTest(unittest.TestCase):
    def testResource(self):
        name   = 'Test Resource'
        resource = Resource(name)
        self.assert_(resource.get_id() is None)
        self.assert_(resource.get_handle()     == make_handle_from_string(name))
        self.assert_(resource.get_n_children() == 0)
        self.assert_(resource.is_group()       == False)

        attr_name  = 'Testattribute'
        attr_value = 'Works'
        resource.set_attribute(attr_name, attr_value)
        self.assert_(resource.get_attribute(attr_name) == attr_value)
        resource.remove_attribute(attr_name)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
