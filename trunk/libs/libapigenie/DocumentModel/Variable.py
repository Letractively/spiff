class Variable:
    def __init__(self, name, type = None):
        self.id   = -1
        self.name = name
        self.type = type
        self.docs = ''


    def set_id(self, id):
        assert id is not None
        self.id = id


    def get_id(self):
        return self.id


    def get_name(self):
        return self.name


    def set_type(self, type):
        self.type = type


    def get_type(self):
        return self.type


    def set_docs(self, docs):
        self.docs = docs


    def get_docs(self):
        return self.docs
