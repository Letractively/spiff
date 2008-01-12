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
        subscribers = self._manager.get_listeners(uri)
        for package in subscribers:
            package.load()
        if synchronous:
            self._event_bus.emit_sync(uri, args)
        else:
            self._event_bus.emit(uri, args)


    def emit(self, uri, args = None):
        """
        Send an asynchronous signal on the event bus.

        @type  uri: string
        @param uri: A unique identifier (name) for the signal.
        @type  args: object
        @param args: Passed on to subscribers of the signal.
        """
        return self.__emit(uri, args, False)


    def emit_sync(self, uri, args = None):
        """
        Send a synchronous signal on the event bus.

        @type  uri: string
        @param uri: A unique identifier (name) for the signal.
        @type  args: object
        @param args: Passed on to subscribers of the signal.
        """
        return self.__emit(uri, args, True)
