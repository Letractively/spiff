from DBObject import *

class Resource(DBObject):
    def __init__(self, name, handle = None):
        DBObject.__init__(self, name, handle)
        self.__n_children     = 0
        self.__attribute_list = {}

    def is_actor(self):
        return False

    def is_group(self):
        return False

    def set_n_children(self, n_children):
        self.__n_children = int(n_children)

    def get_n_children(self):
        return self.__n_children

    def set_attribute(self, name, value):
        self.__attribute_list[name] = value

    def get_attribute(self, name):
        return self.__attribute_list[name]

    def remove_attribute(self, name):
        if self.__attribute_list.has_key(name):
            del self.__attribute_list[name]

    def set_attribute_list(self, list):
        self.__attribute_list = list

    def get_attribute_list(self):
        return self.__attribute_list


if __name__ == '__main__':
    import unittest

    class ResourceTest(unittest.TestCase):
        def runTest(self):
            name   = 'Test Resource'
            resource = Resource(name)
            assert resource.get_id()         == -1
            assert resource.get_handle()     == make_handle_from_string(name)
            assert resource.get_n_children() == 0
            assert resource.is_actor()       == False
            assert resource.is_group()       == False

            attr_name  = 'Testattribute'
            attr_value = 'Works'
            resource.set_attribute(attr_name, attr_value)
            assert resource.get_attribute(attr_name) == attr_value
            resource.remove_attribute(attr_name)

    testcase = ResourceTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
