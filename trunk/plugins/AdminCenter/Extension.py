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
from string import split

class Extension:
    def __init__(self, api):
        self.api      = api
        self.i18n     = api.get_i18n()
        self.guard    = api.get_guard()
        self.guard_db = api.get_guard_db()


    def on_render_request(self):
        self.api.emit('render_start')

        self.api.render('admin.tmpl')

        self.api.emit('render_end')
