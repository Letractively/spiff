import re

def make_handle_from_string(string):
    #FIXME: Return something that can be used to reproduce the original string.
    string = string.lower().replace(' ', '_')
    regexp = re.compile('[^\w\-_\/\.]+')
    return regexp.sub('', string)


if __name__ == '__main__':
    import unittest

    class FunctionTest(unittest.TestCase):
        def runTest(self):
            foo = 'Some Weird 123 String, with %$[]\/ Stuff'
            bar = 'some_weird_123_string_with_/_stuff'
            res = make_handle_from_string(foo)
            assert res == bar
            res = make_handle_from_string(bar)
            assert res == bar

    testcase = FunctionTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
