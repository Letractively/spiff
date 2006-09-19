from DBObject import *

class Action(DBObject):
    pass


if __name__ == '__main__':
    import unittest

    class ActionTest(unittest.TestCase):
        def runTest(self):
            name   = "Test Action"
            action = Action(name)
            assert action.get_id()     == -1
            assert action.get_name()   == name

    testcase = ActionTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
