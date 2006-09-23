from Container import Container

class File(Container):
    def __init__(self):
        Container.__init__(self)
        self.__lines = []

    def get_string(self):
        """
        Returns the complete file in one string.
        
        @rtype:  string
        @return: The contents of the file.
        """
        complete = ''
        for chunk in self.__lines:
            complete.append(chunk.get_string())
        return complete
