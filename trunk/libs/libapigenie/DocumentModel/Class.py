from Container import Container

class Class(Container):
    def __init__(self, name):
        assert name is not None
        Container.__init__(self)
        self.__name = name
