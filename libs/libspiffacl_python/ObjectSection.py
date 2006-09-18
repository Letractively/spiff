import DBObject

class ObjectSection(DBObject):
    pass


if __name__ == '__main__':
    import unittest

    class ObjectSectionTest(unittest.TestCase):
        def runTest(self):
            name   = "Test ObjectSection"
            section = ObjectSection(name)
            assert section.get_id()   == -1
            assert section.get_name() == name

    testcase = ObjectSectionTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
