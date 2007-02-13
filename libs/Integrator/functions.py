# Copyright (C) 2006 Samuel Abels, http://debain.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import re

handle_re     = '\w+'
operator_re   = '(?:=|>=)'
version_re    = '\d+(?:\.\d+)*'
descriptor_re = '^(%s)(?:(%s)(%s))?$' % (handle_re, operator_re, version_re)
uri_re        = '%s(?::%s(:?/%s)*)?$'  % (handle_re, handle_re, handle_re)


def is_valid_uri(uri):
    regexp = re.compile(uri_re)
    return regexp.match(uri)


def descriptor_parse(descriptor):
    regexp = re.compile(descriptor_re)
    return regexp.match(descriptor)


def version_is_greater(version_a, version_b):
    assert version_a is not None
    assert version_b is not None
    numbers_a = version_a.split('.')
    numbers_b = version_b.split('.')
    len_a     = len(numbers_a)
    len_b     = len(numbers_b)
    if len_a > len_b:
        len_ab = len_a
    else:
        len_ab = len_b

    for i in range(len_ab):
        if i >= len_a:
            numbers_a.append(0)
        if i >= len_b:
            numbers_b.append(0)
        if int(numbers_a[i]) > int(numbers_b[i]):
            return True
        if int(numbers_a[i]) < int(numbers_b[i]):
            return False
    if len_a > len_b:
        return True
    return False


if __name__ == '__main__':
    import unittest

    class FunctionTest(unittest.TestCase):
        def is_valid_uri_test(self):
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

        def descriptor_parse_test(self):
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
                assert descriptor_parse(descriptor)
            for descriptor in invalid:
                #print 'Testing', descriptor
                assert not descriptor_parse(descriptor)

        def version_is_greater_test(self):
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

        def runTest(self):
            self.is_valid_uri_test()
            self.descriptor_parse_test()
            self.version_is_greater_test()

    testcase = FunctionTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
