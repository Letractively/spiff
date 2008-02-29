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
from functions import is_valid_uri

class Api(object):
    """
    Contains command functions that are made available to all packages.
    """

    def __init__(self):
        self._manager = None


    def _activate(self, manager):
        assert manager is not None
        self._manager = manager
        self._on_api_activate()


    def _on_api_activate(self):
        """
        May be overwritten.
        """
        pass
