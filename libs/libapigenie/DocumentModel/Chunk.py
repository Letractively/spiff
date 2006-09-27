from Documentable import Documentable

# A piece of a file.
class Chunk(Documentable):
    name   = 'undefined'
    string = ''

    def __init__(self, string = ''):
        self.id     = -1
        self.string = string


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


    def get_string(self):
        """
        The string from the source file that caused this chunk to be
        generated.
        """
        return self.string
