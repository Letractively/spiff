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
import sys

def check_python_version(min_version, max_version = None):
    name = 'Checking the Python version of the server'
    if sys.version_info < min_version:
        hint = 'The Python version is too old (%s).' % sys.__version__
        return name, False, hint
    if max_version is not None and sys.version_info > max_version:
        hint = 'Unsupported Python version %s.' % sys.__version__
        return name, False, hint
    return name, True, None
