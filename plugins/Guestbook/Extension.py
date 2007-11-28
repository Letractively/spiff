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
from Guestbook import Guestbook
from Posting   import Posting
from DB        import DB

class Extension:
    def __init__(self, api):
        self.api          = api
        self.i18n         = api.get_i18n()
        self.db           = api.get_db()
        self.page         = api.get_session().get_requested_page()
        self.guestbook_db = DB(self.db)


    def install(self):
        return self.guestbook_db.install()


    def __create_guestbook(self, may_edit):
        if not may_edit:
            return (None, [self.i18n('No permission to edit this page.')])
        
        guestbook = Guestbook(self.i18n('New Guestbook'), '')
        if not self.guestbook_db.add_guestbook(guestbook):
            return (None, [self.i18n('List creation failed.')])

        self.page.set_attribute('guestbook_id', guestbook.get_id())
        if not self.api.save_page(self.page):
            return (None, [self.i18n('List assignment failed.')])

        return (guestbook, [])


    def __show_guestbook(self, guestbook, may_edit, errors):
        errors = []
        
        # Retrieve the postings from the database.
        if guestbook is None:
            errors.append(self.i18n('Unable to open guestbook.'))
            guestbook = Guestbook(self.i18n('Error'), '')
            postings   = []
        else:
            postings = self.guestbook_db.get_postings(guestbook)

        # Show the guestbook.
        self.api.render('guestbook.tmpl', guestbook = guestbook,
                                          postings  = postings,
                                          may_edit  = may_edit,
                                          errors    = errors)


    def on_render_request(self):
        self.api.emit('render_start')
        errors = []

        # Collect data.
        list_id  = self.page.get_attribute('guestbook_id')
        edit     = self.api.get_get_data('edit')
        add      = self.api.get_post_data('add')
        save     = self.api.get_post_data('save')
        remove   = self.api.get_post_data('remove')
        item_id  = self.api.get_get_data('item_id')
        may_edit = self.api.get_session().may('edit')

        # Create an empty guestbook, if none exists yet.
        if list_id is None:
            (list, errors) = self.__create_guestbook(may_edit)
        else:
            list = self.guestbook_db.get_guestbook_from_id(list_id)
        
        # Save, if requested by the user.
        if add is not None:
            (item, errors) = self.__add_item(may_edit)
        if delete is not None:
            (item, errors) = self.__delete_item(may_edit)

        # Show the requested page.
        if edit is None:
            self.__show_guestbook(list, may_edit, errors)
        else:
            self.__show_guestbook_editor(list, may_edit, errors)

        self.api.emit('render_end')
