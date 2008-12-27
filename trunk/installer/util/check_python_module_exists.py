# Copyright (C) 2008 Samuel Abels, http://debain.org
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
import sys
from sqlalchemy import *


def to_tuple(version):
    assert version is not None
    return version.replace('-', '.').split('.')

def check_python_module_exists(module_name,
                               min_version = None,
                               max_version = None):
    name   = 'Checking for required Python module %s' % module_name
    hint   = 'The Python module was not found. If it is installed,' \
           + ' please check your sys.path (or PYTHON_PATH).' \
           + "\nYour sys.path currently contains: %s" % sys.path

    # Make sure that the module exists. Note that imp.find_module does not
    # appear to work for modules that were installed as an .egg file, so
    # using __import__ instead.
    try:
        module = __import__(module_name)
    except:
        return name, False, hint

    # Only test for version if the installed module supports this.
    if not '__version__' in module.__dict__:
        hint = 'Warning: Installed module does not provide version' \
             + ' information.'
        return name, True, hint

    # Test for the installed version.
    module_version = to_tuple(module.__version__)
    if min_version is not None and module_version < min_version:
        hint = 'The installed version is too old (%s).' % module.__version__
        return name, False, hint
    if max_version is not None and module_version > max_version:
        hint = 'Only found an unsupported version %s.' % module.__version__
        return name, False, hint

    # Success.
    return name, True, None
