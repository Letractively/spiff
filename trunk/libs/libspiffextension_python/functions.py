import re

handle_re     = '\w+'
operator_re   = '(?:=|>=)'
version_re    = '\d+(?:\.\d+)*'
descriptor_re = '^' + handle_re + '(?:' + operator_re + version_re + ')?$'

def descriptor_is_valid(descriptor):
    regexp = re.compile(descriptor_re)
    return regexp.match(descriptor)


def version_is_greater(version1, version2):
    #FIXME
    pass


def make_temp_dir(dirname, prefix):
    #FIXME
    pass


if __name__ == '__main__':
    import unittest

    class FunctionTest(unittest.TestCase):
        def runTest(self):
            valid = [ 'spiff',
                      'spiff1',
                      'spiff=1',
                      'spiff=1.0',
                      'spiff=1.0.0',
                      'spiff=12.34.56',
                      'spiff>=1',
                      'spiff>=1.0',
                      'spiff>=1.0.0',
                      'spiff>=12.34.56' ]
            invalid = [ '',
                        'spiff1.0',
                        'spiff=',
                        'spiff=.',
                        'spiff==',
                        'spiff==1',
                        'spiff=1.',
                        'spiff=1.0.',
                        'spiff=1..0',
                        'spiff=1.0..0',
                        'spiff1.0=1' ]
            for descriptor in valid:
                #print 'Testing', descriptor
                assert descriptor_is_valid(descriptor)
            for descriptor in invalid:
                #print 'Testing', descriptor
                assert not descriptor_is_valid(descriptor)

    testcase = FunctionTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
