import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testIsValidUri',
             'testDescriptorParse',
             'testVersionIsGreater']
    return unittest.TestSuite(map(FunctionTest, tests))

from functions import *

class FunctionTest(unittest.TestCase):
    def testIsValidUri(self):
        valid = [ 'spiff',
                  'spiff:bla',
                  'spiff:bla/blah',
                  'spiff:bla/blah/blah' ]
        invalid = [ 'spiff:',
                    'spiff/',
                    'spiff:/' ]
        for uri in valid:
            #print 'Testing', uri
            assert is_valid_uri(uri)
        for uri in invalid:
            #print 'Testing', uri
            assert not is_valid_uri(uri)

    def testDescriptorParse(self):
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
            self.assert_(descriptor_parse(descriptor))
        for descriptor in invalid:
            #print 'Testing', descriptor
            self.assertRaises(Exception, descriptor_parse, descriptor)

    def testVersionIsGreater(self):
        versions = [
            '1',
            '1.0',
            '1.0.0',
            '1.0.3.1',
            '2',
            '2.10.3',
            '2.12.2',
            '12.34.56' ]
        for a in range(len(versions)):
            for b in range(len(versions)):
                #print "Testing", versions[a], "against", versions[b]
                if a == b:
                    assert not version_is_greater(versions[a], versions[b])
                    assert not version_is_greater(versions[b], versions[a])
                if a > b:
                    assert version_is_greater(versions[a], versions[b])
                    assert not version_is_greater(versions[b], versions[a])
                if b > a:
                    assert not version_is_greater(versions[a], versions[b])
                    assert version_is_greater(versions[b], versions[a])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
