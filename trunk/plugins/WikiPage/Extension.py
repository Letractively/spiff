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
        self.wiki2html.set_wiki_word_handler(self.__wiki_word_handler)
        self.wiki2html.set_url_handler(self.__wiki_url_handler)


    def __wiki_word_handler(self, url, word):
        alias  = self.api.get_get_data('page')
        # The user is viewing the homepage of his web presence.
        if alias is None:
            url = self.api.get_request_uri(page = [word])
            return (url, word)

        # The user is viewing a sub page of his web presence. Find out if it
        # is a sub-page of this wiki or the wiki homepage.
        handle    = self.page is not None and self.page.get_handle()
        pos       = alias.find('/')
        wiki_home = pos == -1 and handle and handle == alias
        #print "WikiWord:", wiki_home, handle, alias, word

        # If the requested page is a sub-page of a wiki (i.e. not the wiki
        # home), build the alias by cutting the requested path and appending
        # the new component.
        stack = split(alias, '/')
        if wiki_home:
            stack.append(word)
        else:
            stack[-1] = word
        url = self.api.get_request_uri(page = ['/'.join(stack)])
        return (url, word)


    def __wiki_url_handler(self, url, word):
        if url.find(':') == -1:
            url = self.api.get_request_uri(page = [url])
        return (url, word)
        


    def __save_page(self, may_edit):
        i18n = self.i18n

        # Check permissions.
        if not may_edit:
            return (None, [i18n('No permission to save this page.')])

        # Collect data.
        handle      = self.page is not None and self.page.get_handle()
        alias       = self.api.get_get_data('page') or handle
        wiki_markup = self.api.get_post_data('wiki_markup')
        assert alias is not None
        if wiki_markup is None or wiki_markup == '':
            return (None, [i18n('No text was entered...')])

        # Find the name or IP of the current user.
        current_user = self.api.get_login().get_current_user()
        if current_user is not None:
            user_name = current_user.get_handle()
        else:
            user_name = os.environ["REMOTE_ADDR"]

        # Copy the data into a warehouse item.
        item = Item(alias)
        item.set_content(wiki_markup)
        item.set_attribute(user_name = user_name)
        if not self.warehouse.add_file(item):
            msg = i18n('File could not be saved - please contact the author!')
            return (None, [msg])
        return (item, [])


    def __show_revision_history(self, alias, may_edit):
        errors = []
        # Collect data.
        offset = self.api.get_get_data('offset') or 0
        list   = self.warehouse.get_file_list_from_alias(alias,
                                                         True,
                                                         offset,
                                                         20)
        
        # Determine the page name.
        if self.api.get_get_data('page') is None and self.page is not None:
            page_name = self.page.get_name()
        else:
            page_name = split(alias, '/')[-1]

        # Show the page.
        tmpl_args = {
            'name':      page_name,
            'revisions': list,
            'may_edit':  may_edit,
            'errors':    errors
        }
        self.api.render('history.tmpl', **tmpl_args)


    def __show_page(self, item, may_edit):
        revision = self.api.get_get_data('revision')
        errors   = []
        if item is None:
            errors.append(self.i18n('You are editing a new page.'))
        elif revision and int(revision) != int(item.get_revision()):
            errors.append(self.i18n('Requested revision not found, showing'
                                    ' most recent version instead.'))
        elif revision:
            errors.append(self.i18n('Showing old revision %s' % revision))

        # Convert to html.
        assert item.get_filename() is not None
        assert len(item.get_filename()) > 0
        self.wiki2html.read(item.get_filename())
        
        # Show the page.
        tmpl_args = {
            'may_edit': may_edit,
            'html':     Markup(self.wiki2html.html),
            'errors':   errors
        }
        self.api.render('show.tmpl', **tmpl_args)
        

    def __show_editor(self, item, alias, may_edit):
        errors = []
        if not may_edit:
            errors.append(self.i18n('You are not allowed to edit this page.'))
        elif item is None:
            errors.append(self.i18n('You are editing a new page.'))

        # Determine the page name.
        if self.api.get_get_data('page') is None and self.page is not None:
            page_name = self.page.get_name()
        else:
            page_name = split(alias, '/')[-1]

        tmpl_args = {
            'name':         page_name,
            'may_edit':     may_edit,
            'errors':       errors
        }

        # Read the file.
        assert item.get_filename() is not None
        assert len(item.get_filename()) > 0
        infile = open(item.get_filename(), 'r')
        assert infile is not None
        tmpl_args['wiki_markup'] = infile.read()
        infile.close()

        # Show the editor.
        self.api.render('edit.tmpl', **tmpl_args)


    def on_render_request(self):
        self.api.emit('render_start')
        self.api.send_headers()
        errors = []

        # Collect data.
        edit     = self.api.get_get_data('edit')
        save     = self.api.get_post_data('save')
        history  = self.api.get_get_data('history')
        revision = self.api.get_get_data('revision')
        handle   = self.page is not None and self.page.get_handle()
        alias    = self.api.get_get_data('page') or handle
        may_edit = self.api.has_permission('edit')
        item     = None
        if revision is not None:
            item = self.warehouse.get_file_from_alias(alias, int(revision))
        if item is None:
            item = self.warehouse.get_file_from_alias(alias)

        # Save, if requested by the user.
        if save is not None:
            (item, errors) = self.__save_page(may_edit)

        # Show the requested page.
        if history is not None:
            self.__show_revision_history(alias, may_edit)
        elif edit is not None or item is None:
            self.__show_editor(item, alias, may_edit)
        else:
            self.__show_page(item, may_edit)

        self.api.emit('render_end')
