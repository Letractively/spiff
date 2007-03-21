"""
extension:    Apilogue
handle:       spiff_apilogue
version:      0.1
author:       Samuel Abels
author-email: spam2@debain.org
description:  Parse API documentation embedded in source code, edit it online
              in a Wiki, and export it back to the source.
dependency:   spiff
signal:       render_start
              render_end
"""
from ApiGenie import ApiDB

class Extension:
    def __init__(self, api):
        self.api      = api
        self.i18n     = api.get_i18n()


    def on_render_request(self):
        self.api.emit('render_start')
        self.api.send_headers()

        self.api.render('home.tmpl')

        self.api.emit('render_end')
