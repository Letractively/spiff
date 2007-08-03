class WorkflowException(Exception):
    def __init__(self, sender, error):
        """
        Standard exception class.
        
        sender -- the activity that threw the exception.
        error -- string
        """
        Exception.__init__(self, '%s: %s' % (sender.name, error))
        self.sender = sender
