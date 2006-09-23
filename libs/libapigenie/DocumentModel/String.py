from Chunk import Chunk

# A piece of unidentified text in a file.
class String(Chunk):
    def __init__(self, string = ''):
        self.string = string
