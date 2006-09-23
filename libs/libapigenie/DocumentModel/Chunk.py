# A piece of a file.
class Chunk:
    name   = 'undefined'
    string = ''
    docs   = ''

    def __init__(self):
        assert False # Should not be called.


    def get_name(self):
        return self.name


    def set_docs(self, string):
        self.docs = string


    def get_docs(self):
        return self.docs


    def get_string(self):
        return self.string
