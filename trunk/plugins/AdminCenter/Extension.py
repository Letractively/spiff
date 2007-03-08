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
        self.api = api


    def on_render_request(self):
        self.api.emit('render_start')
        self.api.send_headers()

        #FIXME
        self.api.render('templates/admin.tmpl')

        self.api.emit('render_end')
