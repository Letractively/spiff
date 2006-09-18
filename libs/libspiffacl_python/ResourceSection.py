import ObjectSection

class ResourceSection(ObjectSection):
    pass


if __name__ == '__main__':
    import unittest

    class ResourceSectionTest(unittest.TestCase):
        def runTest(self):
            name   = "Test ResourceSection"
            section = ResourceSection(name)
            assert section.get_id()   == -1
            assert section.get_name() == name

    testcase = ResourceSectionTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)

