# A piece of a file.
class Chunk:
    name   = 'undefined'
    string = ''
    docs   = ''

    def __init__(self):
        assert False # Should not be called.


    def get_name(self):
        return self.name


    def get_string(self):
        """
        The string from the source file that caused this chunk to be
        generated.
        """
        return self.string


    def set_docs(self, docs):
        """
        Inserts the API documentation.
        """
        self.docs = docs


    def get_docs(self):
        return self.docs
