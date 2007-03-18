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
import os, string
from whrandom import choice

def random_string(length):
    """
    Generates a random string with the given length.

    @type  length: integer
    @param length: The number of characters in the string.
    @rtype:  string
    @return: The newly generated string.
    """
    chars    = string.letters + string.digits
    sequence = choice(chars)
    for i in range(length - 1):
         sequence += choice(chars)
    return sequence


def random_path(depth):
    """
    Generates a random path name with the given depth, where each component
    consists out of letters and digits.

    @type  depth: integer
    @param depth: The number of components in the path.
    @rtype:  string
    @return: The newly generated path name.
    """
    component_len = 8
    path          = random_string(component_len)
    for i in range(depth - 1):
         path = os.path.join(path, random_string(component_len))
    return path
