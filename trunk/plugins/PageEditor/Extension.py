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
from Content      import Content

class Extension:
    def __init__(self, api):
        self.api        = api
        self.i18n       = api.get_i18n()
        self.integrator = api.get_integrator()
        self.content    = api.get_content_db()
        
        self.__errors = []
        self.__hidden = ['spiff',
                         'spiff_core_admin_center',
                         'spiff_core_user_manager',
                         'spiff_core_page_editor',
                         'spiff_core_extension_manager']


    def _layout_data_handler(self, data):
        extension = self.integrator.get_package_from_name(data)
        if extension is None:
            self.__errors.append(self.i18n('Invalid extension in layout.'))
            return ''
        elif extension.get_handle() in self.__hidden:
            self.__errors.append(self.i18n('Hidden extension in layout.'))
            return ''

        #FIXME: Check permission of the extension!

        return extension.get_handle()


    def __page_save(self):
        i18n = self.i18n

        # Retrieve/check data.
        page_str = self.api.get_get_data('page')
        new      = self.api.get_post_data('create')
        name     = self.api.get_post_data('name')   or ''
        layout   = self.api.get_post_data('layout') or ''
        if name == '':
            self.__errors.append(i18n('Page name is missing'))
        if layout == '':
            self.__errors.append(i18n('Layout is missing'))
        if len(self.__errors) > 0:
            return False

        # Fetch the page from the database, or instanciate a new one.
        if new:
            page   = Content(name)
            parent = page_str and self.api.get_requested_page() or None
        else:
            page = self.api.get_requested_page()
        assert page is not None

        # Check whether the caller has permission to edit this page.
        if not self.api.has_permission('edit_page'):
            err = i18n('Insufficient rights to change this page.')
            self.__errors.append(err)
            return False

        # Parse the layout to replace the extension names by handles.
        parser = LayoutParser(layout)
        parser.set_data_handler(self._layout_data_handler)
        parser.parse()
        if len(self.__errors) > 0:
            return False

        # Save the page.
        page.set_name(name)
        page.set_attribute('layout', parser.layout)
        if new and not self.content.add(parent, page):
            self.__errors.append(i18n('Error while creating the page.'))
        elif not self.content.save(page):
            self.__errors.append(i18n('Error while saving the page.'))
            return False

        self.__errors.append(i18n('Page saved.'))
        self.api.set_requested_page(page)
        return True


    def __page_delete(self):
        i18n = self.i18n

        # Retrieve/check data.
        page = self.api.get_requested_page()
        assert page is not None
        if page.get_handle() == 'default':
            self.__errors.append(i18n('Can not delete the default page'))
            return False

        # Check whether the caller has permission to edit this page.
        if not self.api.has_permission('delete'):
            self.__errors.append(i18n('Insufficient rights to delete this' +
                                      ' page.'))
            return False

        if not self.content.delete(page):
            self.__errors.append(i18n('Error while deleting the page.'))
            return False

        self.__errors.append(i18n('Page deleted.'))
        return True


    def __page_editor_show(self):
        # Save the page, if requested.
        if (self.api.get_post_data('save')   is not None or
            self.api.get_post_data('create') is not None):
            self.__page_save()
        elif self.api.get_post_data('delete') is not None:
            self.__page_delete()

        # Collect data.
        page = self.api.get_requested_page()
        assert page is not None
        is_new_page = self.api.get_get_data('new_page') or False
        if is_new_page:
            page_str = self.api.get_get_data('page')
            name     = self.i18n('New Page')
            layout   = ''
            if page_str is not None and page_str != '':
                name = page_str.split('/')[-1]
        else:
            name   = page.get_name()
            layout = page.get_attribute('layout') or ''
        
        # Retrieve a list of available extensions from the DB.
        extension_list = self.integrator.get_package_list(0, 0)
        extensions     = []
        for extension in extension_list:
            if extension.get_handle() not in self.__hidden:
                extensions.append(extension)

        self.api.render('show.tmpl',
                        name            = name,
                        extensions      = extensions,
                        is_new_page     = is_new_page,
                        may_edit_page   = self.api.has_permission('edit_page'),
                        layout          = layout,
                        errors          = self.__errors)


    def on_render_request(self):
        self.api.emit('render_start')

        self.__page_editor_show()

        self.api.emit('render_end')
