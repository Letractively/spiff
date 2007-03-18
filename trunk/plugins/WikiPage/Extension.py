"""
extension:    Wiki Page
handle:       spiff_core_wiki_page
version:      0.1
author:       Samuel Abels
author-email: spam2@debain.org
description:  This core extension shows normal web pages written in plain text
              with some annotations.
dependency:   spiff
signal:       render_start
              render_end
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../libs/'))
from Warehouse import *

class Extension:
    def __init__(self, api):
        self.api       = api
        self.i18n      = api.get_i18n()
        self.db        = api.get_db()
        self.page      = api.get_requested_page()
        self.warehouse = DB(self.db)


    def on_render_request(self):
        self.api.emit('render_start')
        self.api.send_headers()
        errors = []

        item = self.warehouse.get_file_from_alias(self.page.get_handle())
        if not item:
            errors.append(self.i18n('Page not found!'))

        self.api.render('show.tmpl', page = self.page, errors = errors)
        self.api.emit('render_end')
