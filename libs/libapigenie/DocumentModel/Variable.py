class Variable:
    def __init__(self, name, type = None):
        self.name = name
        self.type = type


    def get_name(self):
        return self.name


    def set_docs(self, string):
        self.docs = string


    def get_docs(self):
        return self.docs


    def set_type(self, type):
        self.type = type


    def get_type(self):
        return self.type
