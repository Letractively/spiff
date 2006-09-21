from DocumentModel import *

# Plain text file.
class TextFile(File):
    def load(self, filename):
        fd = file.open(filename)
        for line in fd:
            chunk = Text(line)
            self.__chunks.append(chunk)
