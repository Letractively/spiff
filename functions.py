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
import os, cgi


def get_request_uri(*args, **kwargs):
    """
    Returns the URL string that the client requested. Also appends the given
    variables to the argument list.
    """
    vars = cgi.parse()
    url  = os.environ["REQUEST_URI"]
    pos  = url.find('?')
    if pos is -1:
        url += '?'
    else:
        url = url[:pos + 1]
    vars.update(kwargs)
    for key in vars:
        if url[-1] != '&' and url[-1] != '?':
            url += '&'
        url += key + '=' + str(vars[key][0])
    return url


def gettext(text):
    """
    Internationalizes the given string.
    """
    #FIXME
    return text
