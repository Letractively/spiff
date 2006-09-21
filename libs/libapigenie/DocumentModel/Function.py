from Chunk import Chunk

# Function definition.
class Function(Chunk):
    def __init__(self, name, args, ret):
        self.__name = name
        self.__args = args
        self.__ret  = ret
