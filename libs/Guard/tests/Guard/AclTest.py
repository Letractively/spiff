import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'Guard'))

def suite():
    tests = ['testAcl']
    return unittest.TestSuite(map(AclTest, tests))

from Acl    import Acl
from Action import Action

class AclTest(unittest.TestCase):
    def testAcl(self):
        actor_id    = 10
        action      = Action("Test Action")
        resource_id = 12
        permit      = True
        acl = Acl(10, action, resource_id, permit)
        assert acl.get_actor_id()    == actor_id
        assert acl.get_action()      == action
        assert acl.get_resource_id() == resource_id
        assert acl.get_permit()      == permit

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
