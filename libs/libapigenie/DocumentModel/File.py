# Complete file.
class File:
    def __init__(self):
        self.__chunks = []

    def load(self, filename):
        """
        Parses the file and stores it's chunks in this object.
        
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert False # Should not be called.

    def get(self):
        """
        Returns the complete file in one string.
        
        @rtype:  string
        @return: The contents of the file.
        """
        complete = ''
        for chunk in self.__chunks:
            complete.append(chunk.get_string())
        return complete
