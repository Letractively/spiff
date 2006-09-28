from Chunk import Chunk

class Directory(Chunk):
    def __init__(self, name):
        Chunk.__init__(self, 'directory', '', name)
