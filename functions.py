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
import os


def request_uri(vars = ''):
    """
    Returns the URL string that the client requested. Also appends the given
    variables to the argument list.
    """
    url = os.environ["REQUEST_URI"]
    if url.find('?') is -1:
        return url + '?' + vars
    return url + '&' + vars


def gettext(text):
    """
    Internationalizes the given string.
    """
    #FIXME
    return text
