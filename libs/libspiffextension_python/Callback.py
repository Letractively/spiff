class Callback:
    def  __init__(self, name, context = None):
        assert name is not None
        self.__name    = name
        self.__context = context

    def get_name(self):
        return self.__name

    def get_context(self):
        return self.__context


if __name__ == '__main__':
    import unittest

    class CallbackTest(unittest.TestCase):
        def runTest(self):
            name     = 'Test Callback'
            context  = 'Test Context'
            callback = Callback(name)
            assert callback.get_name()    == name
            assert callback.get_context() == None
            
            callback = Callback(name, context)
            assert callback.get_name()    == name
            assert callback.get_context() == context

    testcase = CallbackTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
