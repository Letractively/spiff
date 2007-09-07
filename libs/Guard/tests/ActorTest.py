import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testActor']
    return unittest.TestSuite(map(ActorTest, tests))

from functions import make_handle_from_string
from Actor     import Actor

class ActorTest(unittest.TestCase):
    def testActor(self):
        name   = 'Test Actor'
        actor = Actor(name)
        assert actor.get_id()     == -1
        assert actor.get_name()   == name
        assert actor.get_handle() == make_handle_from_string(name)
        assert actor.is_actor()   == True
        
        pwd = 'Testpwd'
        actor.set_auth_string(pwd)
        assert actor.has_auth_string(pwd)         == True
        assert actor.has_auth_string('incorrect') == False

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
