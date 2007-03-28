"""
extension:    Layout Editor
handle:       spiff_core_layout_editor
version:      0.1
author:       Samuel Abels
author-email: spam2@debain.org
description:  This core extension implements the user interface for editing
              the layout of a site.
dependency:   spiff
signal:       render_start
              render_end
"""
from string import split
from Layout import Layout

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

        # Parse the layout and retrieve all extension handles.
        page = self.api.get_requested_page()
        assert page is not None
        page.set_attribute('layout', layout)
        layout = Layout(object, page)
        assert layout is not None

        # Make sure that no invalid (i.e. core) extensions are contained
        # in the layout, and that the user has view permissions on all
        # extensions.
        for handle in layout.get_extension_handles():
            if handle in self.__hidden:
                errors.append(i18n('Invalid extension %s in layout' % handle))
                return errors
            #FIXME: Check permission of these extensions

        # Save the layout.
        #FIXME: self.api.save_page(page)
        return []


    def __layout_editor_show(self, errors = []):
        page = self.api.get_requested_page()
        assert page is not None
        layout = page.get_attribute('layout') or '';
        
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
