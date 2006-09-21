from Chunk import Chunk

# A piece of unidentified text in a file.
class String(Chunk):
    def __init__(self, string = ''):
        self.__string = string

    def get_string(self):
        return self.__string
