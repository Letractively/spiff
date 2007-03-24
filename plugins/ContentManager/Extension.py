"""
extension:    Content Manager
handle:       spiff_core_content_manager
version:      0.1
author:       Samuel Abels
author-email: spam2@debain.org
description:  This core extension implements the user interface for
              managing content.
dependency:   spiff
signal:       render_start
              render_end
"""
from string import split

class Extension:
    def __init__(self, api):
        self.api        = api
        self.i18n       = api.get_i18n()
        self.integrator = api.get_integrator()


    def on_render_request(self):
        self.api.emit('render_start')
        self.api.send_headers()
        hidden = ['spiff',
                  'spiff_core_admin_center',
                  'spiff_core_user_manager',
                  'spiff_core_content_manager']

        extension_list = self.integrator.get_extension_info_list(0, 0)
        extensions     = []
        for extension in extension_list:
            if extension.get_handle() not in hidden:
                extensions.append(extension)

        self.api.render('content_editor.tmpl', extensions = extensions)

        self.api.emit('render_end')
