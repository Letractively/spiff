from Container import Container

# Function definition.
class Function(Container):
    def __init__(self, name, args, ret):
        self.__name = name
        self.__args = args
        self.__ret  = ret
