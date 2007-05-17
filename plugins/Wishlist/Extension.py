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
import sys
from Wishlist import Wishlist
from Wish     import Wish
from DB       import DB

class Extension:
    def __init__(self, api):
        self.api         = api
        self.i18n        = api.get_i18n()
        self.db          = api.get_db()
        self.page        = api.get_requested_page()
        self.wishlist_db = DB(self.db)


    def install(self):
        return self.wishlist_db.install()


    def __create_wishlist(self, may_edit):
        if not may_edit:
            return [self.i18n('You are not allowed to edit this page.')]
        
        wishlist = Wishlist(self.i18n('New Wishlist'), '')
        list     = self.wishlist_db.add_wishlist(wishlist)
        if list is None:
            return [self.i18n('List creation failed.')]

        self.page.set_attribute('wishlist_id', list.get_id())

        return (list, [])


    def __show_wishlist(self, list, may_edit, errors):
        errors = []
        
        # Retrieve the wishes from the database.
        if list is None:
            errors.append(self.i18n('Unable to open wishlist.'))
        else:
            wishes = self.wishlist_db.get_wishes(list)

        # Show the wishlist.
        self.api.render('wishlist.tmpl', wishlist = wishlist,
                                         wishes   = wishes,
                                         may_edit = may_edit,
                                         errors   = errors)


    def on_render_request(self):
        self.api.emit('render_start')
        errors = []

        # Collect data.
        list_id  = self.page.get_attribute('wishlist_id')
        add      = self.api.get_post_data('add')
        delete   = self.api.get_post_data('delete')
        item_id  = self.api.get_get_data('item_id')
        may_edit = self.api.has_permission('edit')

        # Create an empty wishlist, if none exists yet.
        if list_id is None:
            (list, errors) = self.__create_wishlist(may_edit)
        else:
            list = self.wishlist_db.get_wishlist_from_id(list_id)
        
        # Save, if requested by the user.
        if add is not None:
            (item, errors) = self.__add_item(may_edit)
        if save is not None:
            (item, errors) = self.__save_item(may_edit)

        # Show the requested page.
        self.__show_wishlist(may_edit, errors)

        self.api.emit('render_end')
