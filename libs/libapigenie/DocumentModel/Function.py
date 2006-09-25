from Container import Container

# Function definition.
class Function(Container):
    def __init__(self, string, name):
        assert string is not None
        assert name   is not None
        Container.__init__(self, string)
        self.name = name
        self.args = {}
        self.ret  = None


    def add_arg(self, arg):
        self.args[arg.get_name()] = arg


    def has_arg(self, name):
        return self.args.has_key(name)


    def get_arg(self, name):
        return self.args[name]


    def get_arg_list(self):
        return self.args


    def set_return(self, var):
        self.ret = var


    def get_return(self):
        return self.ret
