class Documentable:
    def set_docs(self, docs):
        """
        Attaches documentation.
        """
        self.docs = docs


    def get_docs(self):
        """
        Returns the documentation that is atteched to this file.
        """
        return self.docs
