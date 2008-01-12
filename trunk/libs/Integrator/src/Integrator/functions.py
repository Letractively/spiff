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
from Exception import InvalidDescriptor

handle_re     = '\w+'
operator_re   = '(?:=|>=)'
version_re    = '\d+(?:\.\d+)*'
descriptor_re = '^(%s)(?:(%s)(%s))?$' % (handle_re, operator_re, version_re)
uri_re        = '%s(?::%s(:?/%s)*)?$'  % (handle_re, handle_re, handle_re)


def is_valid_uri(uri):
    regexp = re.compile(uri_re)
    return regexp.match(uri)


def descriptor_parse(descriptor):
    regexp  = re.compile(descriptor_re)
    match   = regexp.match(descriptor)
    if match is None:
        raise InvalidDescriptor(descriptor)
    handle  = match.group(1)
    op      = match.group(2)
    version = match.group(3)
    if op is None:
        op       = '>='
        version  = '0'
    return handle, op, version


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
