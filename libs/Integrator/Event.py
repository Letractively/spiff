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

class Event(object):
    """
    Events are used only internally by the event bus, to queue them up
    when emitted synchronously.
    """
    def __init__(self, uri, args):
        """
        @type  uri: string
        @param uri: The URI of the signal. Can be a regular expression.
        @type  args: object
        @param args: Any arguments that are passed to the listeners.
        """
        self.__uri  = uri
        self.__args = args

    def get_uri(self):
        return self.__uri

    def get_args(self):
        return self.__args
