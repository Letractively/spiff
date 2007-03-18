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
use_mod_rewrite = False


def get_request_uri(*args, **kwargs):
    """
    Returns the URL string that the client requested. Also appends the given
    variables to the argument list.
    """
    vars = cgi.parse()
    url  = os.environ["REQUEST_URI"]
    page = vars.get('page', [''])[0]

    # The "page" variable is treated differently depending on whether
    # mod_rewrite is enabled. Firstly, remove it from the dictionaries.
    vars.update(kwargs)
    if vars.has_key('page'):
        page = vars['page'][0]
        del vars['page']

    # Remove all attributes that are None.
    for key in vars.keys():
        if vars[key] is None:
            del vars[key]

    # Build the path of the URL.
    if use_mod_rewrite:
        url = '/' + page + '/'
        if len(vars) > 0:
            url += '?'
    else:
        pos = url.find('?')
        if pos != -1:
            url = url[:pos]
        if page != '':
            url += '?page=' + page
        elif len(vars) > 0:
            url += '?'

    # Append attributes, if any.
    for key in vars:
        if url[-1] != '&' and url[-1] != '?':
            url += '&'
        url += key + '=' + str(vars[key][0])
    return url


def get_mod_rewrite_prevented_uri(plugin_dir):
    """
    Returns a URL that points to the same directory as the given one,
    but where, when mod_rewrite is enabled, rewriting is prevented.
    """
    if not use_mod_rewrite:
        return plugin_dir
    return "mod-rewrite-will-strip-this/" + plugin_dir


def gettext(text):
    """
    Internationalizes the given string.
    """
    #FIXME
    return text
