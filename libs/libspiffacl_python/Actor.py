from Resource import *
import random
import time
import base64
import sha

class Actor(Resource):
    def __init__(self, name, handle = None):
        Resource.__init__(self, name, handle)
        self.__salt_length = 4
        self.set_auth_string('')

    def is_actor(self):
        return True

    def set_auth_string(self, auth_string):
        salt = sha.new(str(time.time) + str(random.random())).hexdigest()
        salt = base64.encodestring(salt)
        salt = salt[0:self.__salt_length]
        hash = salt + sha.new(auth_string + salt).hexdigest()
        self.set_attribute('auth_hash', hash)

    def has_auth_string(self, auth_string):
        auth_hash = self.get_attribute('auth_hash')
        salt      = auth_hash[0:self.__salt_length]
        hash      = auth_hash[self.__salt_length:]
        return sha.new(auth_string + salt).hexdigest() == hash


if __name__ == '__main__':
    import unittest

    class ActorTest(unittest.TestCase):
        def runTest(self):
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

    testcase = ActorTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
