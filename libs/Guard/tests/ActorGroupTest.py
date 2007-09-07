import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testActorGroup']
    return unittest.TestSuite(map(ActorGroupTest, tests))

from functions  import make_handle_from_string
from ActorGroup import ActorGroup

class ActorGroupTest(unittest.TestCase):
    def testActorGroup(self):
        name   = 'Test ActorGroup'
        actor_group = ActorGroup(name)
        assert actor_group.get_id()     == -1
        assert actor_group.get_name()   == name
        assert actor_group.get_handle() == make_handle_from_string(name)
        assert actor_group.is_group()   == True
        
        pwd = 'Testpwd'
        actor_group.set_auth_string(pwd)
        assert actor_group.has_auth_string(pwd)         == False
        assert actor_group.has_auth_string('incorrect') == False

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
