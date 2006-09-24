import re

def int2hex(n, len):
    assert n   is not None
    assert len is not None
    hexval = ('0' * len) + "%x" % int(n)
    return hexval[len * -1:]


def make_handle_from_string(string):
    #FIXME: Return something that can be used to reproduce the original string.
    string = string.lower().replace(' ', '_')
    regexp = re.compile('[^\w\-_\/\.]+')
    return regexp.sub('', string)


if __name__ == '__main__':
    import unittest

    class FunctionTest(unittest.TestCase):
        def runTest(self):
            # int2hex()
            assert int2hex(10, 8) == '0000000a'

            # make_handle_from_string()
            foo = 'Some Weird 123 String, with %$[]\/ Stuff'
            bar = 'some_weird_123_string_with_/_stuff'
            res = make_handle_from_string(foo)
            assert res == bar
            res = make_handle_from_string(bar)
            assert res == bar

    testcase = FunctionTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
