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

class Form:
    next_button, \
    cancel_button = range(2)
    caption = {
      next_button:   'Next',
      cancel_button: 'Cancel'
    }


    def __init__(self, markup, buttons):
        assert markup  is not None
        assert buttons is not None
        assert type(buttons) == type([])
        self.__markup  = markup
        self.__buttons = buttons


    def get_markup(self):
        return self.__markup


    def get_buttons(self):
        return self.__buttons
