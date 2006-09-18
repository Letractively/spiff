import ObjectSection

class ActionSection(ObjectSection):
    pass


if __name__ == '__main__':
    import unittest

    class ActionSectionTest(unittest.TestCase):
        def runTest(self):
            name   = "Test ActionSection"
            section = ActionSection(name)
            assert section.get_id()   == -1
            assert section.get_name() == name

    testcase = ActionSectionTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
