import Resource

class ResourceGroup(Resource):
    def is_group(self):
        return True


if __name__ == '__main__':
    import unittest

    class ResourceGroupTest(unittest.TestCase):
        def runTest(self):
            name  = "Test ResourceGroup"
            group = ResourceGroup(name)
            assert group.get_id()   == -1
            assert group.get_name() == name
            assert group.is_group() == True

    testcase = ResourceGroupTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
