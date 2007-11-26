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

def int2bin(number):
    return struct.pack('l', number)


def hex2bin(hex):
    assert len(hex) <= 8
    return int2bin(string.atol(hex, 16))


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
    numbers  = bin_path2list(path)
    hex_path = ''
    for number in numbers:
        hex_path += int2hex(number, 8)
    #print "PATH: '" + hex_path + "', Len:", len(hex_path)
    return hex_path


def list2hex_path(path):
    assert path is not None
    #print "Path length:", len(path)
    hex_path = ''
    for number in path:
        hex_path += int2hex(number, 8)
    return hex_path


def list2bin_path(path):
    assert path is not None
    #print "Path length:", len(path)
    bin_path = ''
    for number in path:
        bin_path += struct.pack('l', int(number))
    return bin_path


def bin_path2list(path):
    assert path is not None
    #print "Path length:", len(path)
    numbers = []
    while path != '':
        cur_chunk = path[:4]
        numbers.append(struct.unpack('l', cur_chunk)[0])
        path = path[4:]
    return numbers


def int2hex(n, len):
    assert n   is not None
    assert len is not None
    hexval = ('0' * len) + "%x" % int(n)
    return hexval[len * -1:]


def make_handle_from_string(name):
    name   = name.lower().replace(' ', '_')
    regexp = re.compile('[^\w\-_\/\.]+')
    return regexp.sub('', name)
