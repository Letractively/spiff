from Chunk import Chunk

class Container(Chunk):
    def __init__(self, string = ''):
        Chunk.__init__(self, string)
        self.children = []


    def add_child(self, child):
        assert child is not None
        self.children.append(child)


    def get_child_list(self):
        return self.children


    def get_string(self):
        """
        Returns the complete chunk (including all children) in one string.
        
        @rtype:  string
        @return: The contents of the file.
        """
        complete = self.string
        for child in self.children:
            complete += child.get_string()
        return complete
