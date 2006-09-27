from Documentable import Documentable

class Directory(Documentable):
    def __init__(self, name):
        self.id   = -1
        self.name = name


    def set_id(self, id):
        assert id is not None
        self.id = id


    def get_id(self):
        return self.id


    def get_name(self):
        """
        Returns the name of this chunk.
        """
        return self.name
