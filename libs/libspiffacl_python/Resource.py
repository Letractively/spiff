import DBObject

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

    def set_attribute_list(self, list):
        self.__attribute_list = list

    def get_attribute_list(self):
        return self.__attribute_list
