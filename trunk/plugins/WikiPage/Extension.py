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
import re
import sys
from string import split
sys.path.append(os.path.join(os.path.dirname(__file__), '../../libs/'))
from Warehouse  import *
from WikiMarkup import *
from genshi     import Markup

class Extension:
    def __init__(self, api):
        self.wiki_word_re = re.compile("(?:-&gt;(\w+)|([A-Z]\w+[A-Z]\w+))")
        self.is_recursive = True
        self.api          = api
        self.i18n         = api.get_i18n()
        self.db           = api.get_db()
        self.page         = api.get_requested_page()
        self.wiki2html    = Wiki2Html()
        self.warehouse    = DB(self.db)
        root_directory    = os.path.dirname(sys.argv[0])
        data_directory    = os.path.join(root_directory, 'data', 'warehouse')
        self.warehouse.set_directory(data_directory)


    def install(self):
        #FIXME: Install the WikiCommands page.
        pass


    def __wiki_word2link(self, match):
        # This is a callback function for a regular expression substitution.
        word   = match.groups()[0] or match.groups()[1]
        handle = self.page is not None and self.page.get_handle()
        alias  = self.api.get_get_data('page') or handle
        if alias is None:
            url = self.api.get_request_uri(page = [word])
        else:
            if alias.find('/') != -1:
                stack = split(alias, '/')
                alias = '/'.join(stack[:-1])
            url   = self.api.get_request_uri(page = [alias + '/' + word])
        return '<a href="%s">%s</a>' % (url, word)


    def __save_page(self):
        i18n = self.i18n
        handle      = self.page is not None and self.page.get_handle()
        alias       = self.api.get_get_data('page') or handle
        wiki_markup = self.api.get_post_data('wiki_markup')
        assert alias is not None
        if wiki_markup is None or wiki_markup == '':
            return [i18n('No text was entered...')]

        item = Item(alias)
        item.set_content(wiki_markup)
        if not self.warehouse.add_file(item):
            msg = i18n('File could not be saved - please contact the author!')
            return (None, [msg])
        return (item, [])


    def on_render_request(self):
        self.api.emit('render_start')
        self.api.send_headers()
        errors = []

        # Collect data.
        edit     = self.api.get_get_data('edit')
        save     = self.api.get_post_data('save')
        revision = self.api.get_get_data('revision')
        handle   = self.page is not None and self.page.get_handle()
        alias    = self.api.get_get_data('page') or handle
        may_edit = self.api.has_permission('edit')
        item     = None
        if self.page is None:
            name = split(alias, '/')[-1]
        else:
            name = self.page.get_name()
        if not may_edit and edit is not None:
            errors.append(self.i18n('You are not allowed to edit this page.'))
        if revision is not None:
            item = self.warehouse.get_file_from_alias(alias, int(revision))
        if item is None:
            item = self.warehouse.get_file_from_alias(alias)
        if (item is not None
            and revision is not None
            and revision != item.get_revision()):
            errors.append(self.i18n('Requested revision not found, showing '
                                    'most recent version instead.'))

        # Save, if requested by the user.
        if save is not None:
            (item, errors) = self.__save_page()

        tmpl_args = {
            'name':         name,
            'may_edit':     may_edit,
            'errors':       errors
        }

        # Edit an existing page.
        if item is not None and edit is not None:
            assert item.get_filename() is not None
            assert len(item.get_filename()) > 0

            # Read the file.
            infile = open(item.get_filename(), 'r')
            assert infile is not None
            tmpl_args['wiki_markup'] = infile.read()
            infile.close()

            self.api.render('edit.tmpl', **tmpl_args)

        # Edit a new page.
        elif item is None:
            errors.append(self.i18n('You are editing a new page.'))
            self.api.render('edit.tmpl', **tmpl_args)

        # Show a page.
        else:
            assert item.get_filename() is not None
            assert len(item.get_filename()) > 0
            
            # Convert to html.
            self.wiki2html.read(item.get_filename())
            html = self.wiki_word_re.sub(self.__wiki_word2link,
                                         self.wiki2html.html)
            tmpl_args['html'] = Markup(html)
            
            self.api.render('show.tmpl', **tmpl_args)
        self.api.emit('render_end')
