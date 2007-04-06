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
from string       import split
from LayoutParser import LayoutParser

class Extension:
    def __init__(self, api):
        self.api        = api
        self.i18n       = api.get_i18n()
        self.guard      = api.get_guard()
        self.guard_db   = api.get_guard_db()
        self.integrator = api.get_integrator()

        self.__hidden = ['spiff',
                         'spiff_core_admin_center',
                         'spiff_core_user_manager',
                         'spiff_core_layout_editor']


    def _layout_data_handler(self, data):
        extension = self.integrator.get_extension_info_from_name(data)
        assert extension is not None
        assert extension.get_handle() not in self.__hidden

        #FIXME: Check permission of the extension!

        return extension.get_handle()


    def __layout_save(self):
        errors = []
        i18n   = self.i18n

        # Retrieve/check data.
        layout = self.api.get_post_data('layout')
        if layout is None or layout == '':
            errors.append(i18n('Layout is missing'))
        if len(errors) > 0:
            return errors

        # Check whether the caller has permission to edit this page.
        if not self.api.has_permission('edit_layout'):
            errors.append(i18n('Insufficient rights to change the layout.'))
            return errors

        # Parse the layout to replace the extension names by handles.
        parser = LayoutParser(layout)
        parser.set_data_handler(self._layout_data_handler)
        parser.parse()

        # Save the layout.
        page = self.api.get_requested_page()
        assert page is not None
        page.set_attribute('layout', parser.layout)
        if not self.api.save_page(page):
            errors.append(i18n('Error while saving layout.'))

        return errors


    def __layout_editor_show(self, errors = []):
        page = self.api.get_requested_page()
        assert page is not None
        layout = page.get_attribute('layout') or ''
        
        # Retrieve a list of available extensions from the DB.
        extension_list = self.integrator.get_extension_info_list(0, 0)
        extensions     = []
        for extension in extension_list:
            if extension.get_handle() not in self.__hidden:
                extensions.append(extension)

        self.api.render('layout_editor.tmpl',
                        name       = page.get_name(),
                        extensions = extensions,
                        layout     = layout,
                        errors     = errors)


    def on_render_request(self):
        self.api.emit('render_start')

        if self.api.get_post_data('save') is not None:
            errors = self.__layout_save()
            self.__layout_editor_show(errors)
        else:
            self.__layout_editor_show()

        self.api.emit('render_end')
