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
import string
import struct

def hex_path2bin_path(path):
    assert path is not None
    bin_path = ''
    #print "PATH: '" + path + "', Len:", len(path)
    while path != '':
        #print "Path: '" + path[-8:] + "', Len:", len(path[-8:])
        cur_id    = string.atol(path[-8:], 16)
        bin_path += struct.pack('l', cur_id)
        path = path[0:len(path) - 8]
    return bin_path


def bin_path2hex_path(path):
    assert path is not None
    #print "Path length:", len(path)
    numbers = []
    while path != '':
        cur_chunk = path[-4:]
        numbers.append(struct.unpack('l', cur_chunk)[0])
        path = path[0:len(path) - 4]
    hex_path = ''
    for number in numbers:
        hex_path += int2hex(number, 8)
    #print "PATH: '" + hex_path + "', Len:", len(hex_path)
    return hex_path


def int2hex(n, len):
    assert n   is not None
    assert len is not None
    hexval = ('0' * len) + "%x" % int(n)
    return hexval[len * -1:]


def make_handle_from_string(name):
    #FIXME: Return something that can be used to reproduce the original string.
    name   = name.lower().replace(' ', '_')
    regexp = re.compile('[^\w\-_\/\.]+')
    return regexp.sub('', name)


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
