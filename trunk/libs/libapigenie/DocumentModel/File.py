from Container import Container

class File(Container):
    def __init__(self, name):
        Container.__init__(self, '')
        self.name = name
