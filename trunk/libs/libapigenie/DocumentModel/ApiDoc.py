from Chunk import Chunk

class ApiDoc(Chunk):
    def __init__(self, data):
        Chunk.__init__(self, 'api_doc', data, '')
        self.introduction = ''
        self.description  = ''
        self.arguments    = []
        self.argument_map = {}
        self.return_var   = None

    def set_introduction(self, introduction):
        self.introduction = introduction

    def get_introduction(self):
        return self.introduction

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    def add_argument(self, arg):
        self.arguments.append(arg)
        self.argument_map[arg.get_name()] = arg

    def get_argument(self, name):
        if not self.argument_map.has_key(name):
            return None
        return self.argument_map[name]

    def get_argument_list(self):
        return self.arguments

    def set_return(self, var):
        self.return_var = var

    def get_return(self):
        return self.return_var
