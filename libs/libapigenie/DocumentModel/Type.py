class Type:
    def __init__(self, name):
        self.__name        = name
        self.__inheritance = []

    def add_inheritance(self, type):
        self.__inheritance.append(type)

    def get_inheritance(self):
        """
        @rtype:  list[Type]
        @return: A list of all types from which this type inherits directly.
        """
        return self.__inheritance
