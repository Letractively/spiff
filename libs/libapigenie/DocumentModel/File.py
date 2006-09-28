from Chunk import Chunk

class File(Chunk):
    def __init__(self, name):
        Chunk.__init__(self, 'file', '', name)
