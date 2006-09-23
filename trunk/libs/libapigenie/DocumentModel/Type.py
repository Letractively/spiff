from Chunk import Chunk

class Type(Chunk):
    def __init__(self, name):
        self.name        = name
        self.inheritance = []

    def add_inheritance(self, type):
        self.inheritance.append(type)

    def get_inheritance(self):
        """
        @rtype:  list[Type]
        @return: A list of all types from which this type inherits directly.
        """
        return self.inheritance
