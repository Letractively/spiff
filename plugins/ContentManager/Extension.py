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
        self.api      = api
        self.i18n     = api.get_i18n()
        self.guard    = api.get_guard()
        self.guard_db = api.get_guard_db()


    def on_render_request(self):
        self.api.emit('render_start')
        self.api.send_headers()

        self.api.render('content_editor.tmpl')

        self.api.emit('render_end')
