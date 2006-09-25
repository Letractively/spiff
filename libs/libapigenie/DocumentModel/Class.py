from Container import Container

class Class(Container):
    def __init__(self, string, name):
        assert string is not None
        assert name   is not None
        Container.__init__(self, string)
        self.name     = name
        self.inherits = {}
        self.methods  = {}


    def add_method(self, func):
        self.add_child(func)
        self.methods[func.get_name()] = func


    def get_method(self, name):
        return self.methods[name]
