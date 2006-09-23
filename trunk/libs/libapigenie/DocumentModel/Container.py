from Chunk import Chunk

class Container(Chunk):
    def __init__(self):
        self.__children = []
    
    def add_child(self, child):
        assert child is not None
        self.__children.append(child)

    def get_child_list(self):
        return self.__children
