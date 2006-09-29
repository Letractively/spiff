from Chunk import Chunk

class ApiDoc(Chunk):
    def __init__(self, data, generator = None):
        Chunk.__init__(self, 'api_doc', data, '')
        self.introduction = ''
        self.description  = ''
        self.arguments    = []
        self.argument_map = {}
        self.return_var   = None
        self.generator    = generator
        self.modified     = False

    def attach_generator(self, generator):
        self.generator = generator

    def set_introduction(self, introduction):
        self.modified = True
        self.introduction = introduction

    def get_introduction(self):
        return self.introduction

    def set_description(self, description):
        self.modified = True
        self.description = description

    def get_description(self):
        return self.description

    def add_argument(self, arg):
        self.modified = True
        self.arguments.append(arg)
        self.argument_map[arg.get_name()] = arg

    def get_argument(self, name):
        if not self.argument_map.has_key(name):
            return None
        return self.argument_map[name]

    def get_argument_list(self):
        return self.arguments

    def set_return(self, var):
        self.modified = True
        self.return_var = var

    def get_return(self):
        return self.return_var

    def add_child(self, child):
        assert False # This is a stub.

    def get_data(self):
        if not self.modified:
            return self.data
        if self.generator is None:
            return self.data
        return self.generator.get_data(self)
        
    def mark_unmodified(self):
        self.modified = False
