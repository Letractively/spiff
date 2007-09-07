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

class Api:
    def __init__(self):
        self._manager = None


    def activate(self, manager):
        assert manager is not None
        self._manager   = manager
        self._event_bus = manager.event_bus
        self._on_api_activate()


    def _on_api_activate(self):
        """
        May be overwritten.
        """
        pass


    def __emit(self, uri, args, synchronous):
        assert is_valid_uri(uri)
        #FIXME: Check signal permissions!
        self._manager.load_extension_from_event(uri)
        if synchronous:
            self._event_bus.emit_sync(uri, args)
        else:
            self._event_bus.emit(uri, args)


    def emit(self, uri, args = None):
        return self.__emit(uri, args, False)


    def emit_sync(self, uri, args = None):
        return self.__emit(uri, args, True)
