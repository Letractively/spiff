import Action

class Acl():
    def __init__(self, actor_id, action, resource_id, permit = False):
        self.__actor_id    = int(actor_id)
        self.__action      = action
        self.__resource_id = int(resource_id)
        self.__permit      = bool(permit)

    def set_actor_id(self, actor_id):
        self.__actor_id = int(actor_id)

    def get_actor_id(self):
        return self.__actor_id

    def set_acl(self, acl):
        self.__action = action

    def get_acl(self):
        return self.__action

    def set_resource_id(self, resource_id):
        self.__resource_id = int(resource_id)

    def get_resource_id(self):
        return self.__resource_id

    def set_permit(self, permit):
        self.__permit = bool(permit)

    def get_permit(self):
        return self.__permit


if __name__ == '__main__':
    import unittest

    class AclTest(unittest.TestCase):
        def runTest(self):
            actor_id    = 10
            action      = Action("Test Action")
            resource_id = 12
            permit      = True
            acl = Acl(10, action, resource_id, permit)
            assert acl.get_actor_id()    == actor_id
            assert acl.get_action()      == action
            assert acl.get_resource_id() == resource_id
            assert acl.get_permit()      == permit

    testcase = AclTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
