from Container import Container

class File(Container):
    def __init__(self, filename):
        Container.__init__(self)
        self.name = filename
