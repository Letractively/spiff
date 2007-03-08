"""
extension:    Admin Center
handle:       spiff_core_admin_center
version:      0.1
author:       Samuel Abels
author-email: spam2@debain.org
description:  This core extension implements the admininistration user interface.
dependency:   spiff spiff_core_login
signal:       render_start
              render_end
"""
class Extension:
    def __init__(self, api):
        self.api   = api
        self.guard = api.get_guard()


    def __content_editor(self):
        if self.api.get_form_value('submit') is not None:
            pass #FIXME
        else:
            self.api.render('templates/content_editor.tmpl')


    def __user_editor(self):
        gid = self.api.get_form_value('gid')
        uid = self.api.get_form_value('uid')
        if uid is not None:
            user = self.guard.get_resource_from_id(uid)
            self.api.render('templates/user_editor.tmpl', user = user)
        elif gid is not None:
            group = self.guard.get_resource_from_id(gid)
            self.api.render('templates/group_editor.tmpl', group = group)
        else:
            group = self.guard.get_resource_from_handle('everybody', 'users')
            self.api.render('templates/group_editor.tmpl', group = group)


    def on_render_request(self):
        self.api.emit('render_start')
        self.api.send_headers()

        if self.api.get_form_value('manage_content') is not None:
            self.__content_editor()
        elif self.api.get_form_value('manage_users') is not None:
            self.__user_editor()
        else:
            self.api.render('templates/admin.tmpl')

        self.api.emit('render_end')
