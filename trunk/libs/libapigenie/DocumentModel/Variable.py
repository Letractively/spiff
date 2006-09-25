from Documentable import Documentable

class Variable(Documentable):
    def __init__(self, name, type = None):
        self.name = name
        self.type = type


    def get_name(self):
        return self.name


    def set_type(self, type):
        self.type = type


    def get_type(self):
        return self.type
