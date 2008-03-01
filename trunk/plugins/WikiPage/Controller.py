# Copyright (C) 2006 Samuel Abels, http://debain.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import os
import re
import sys
from genshi              import Markup
from string              import split
from ExtensionController import ExtensionController
from Wiki                import Wiki

def check_cache(api, api_key):
    if api.get_post_data('save') is not None:
        api.flush_cache(api_key)
        return False
    return True

class Controller(ExtensionController):
    def __init_wiki(self):
        wiki = Wiki(self.api.get_db(),
                    wiki_word_handler = self.__wiki_word_handler,
                    wiki_url_handler  = self.__wiki_url_handler)
        wiki.set_directory(os.path.join(self.api.get_data_dir(), 'warehouse'))
        return wiki


    def __get_alias(self):
        page   = self.api.get_session().get_requested_page()
        handle = page is not None and page.get_handle()
        return self.api.get_get_data('page') or handle


    def __get_page_name(self):
        page = self.api.get_session().get_requested_page()
        if self.api.get_get_data('page') is None and page is not None:
            return page.get_name()
        return split(self.__get_alias(), '/')[-1]


    def __get_user(self):
        # Find the name or IP of the current user.
        current_user = self.api.get_session().get_user()
        if current_user is not None:
            return current_user.get_handle()
        return os.environ["REMOTE_ADDR"]


    def __wiki_word_handler(self, url, word):
        alias = self.api.get_get_data('page')

        # The user is viewing the homepage of his web presence.
        if alias is None:
            url = self.api.get_requested_uri(page     = [word],
                                             revision = None,
                                             action   = None)
            return (url, word)

        # The user is viewing a sub page of his web presence. Find out if it
        # is a sub-page of this wiki or the wiki homepage.
        page      = self.api.get_session().get_requested_page()
        handle    = page is not None and page.get_handle()
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
        url = self.api.get_requested_uri(page     = ['/'.join(stack)],
                                         revision = None,
                                         action   = None)
        return (url, word)


    def __wiki_url_handler(self, url, word):
        if url.find(':') == -1:
            url = self.api.get_requested_uri(page     = [url],
                                             revision = None,
                                             action   = None)
        return (url, word)


    def save(self, **kwargs):
        if kwargs.has_key('cancel'):
            return self.index()

        wiki     = self.__init_wiki()
        i18n     = self.api.get_i18n()
        may_edit = self.api.get_session().may('edit_content')
        alias    = self.__get_alias()
        user     = self.__get_user()
        
        # Save.
        if not may_edit:
            errors = [i18n('No permission to save this page.')]
        elif kwargs.get('wiki_markup', '') == '':
            errors = [i18n('No text was entered...')]
        elif not wiki.save_page(alias, kwargs.get('wiki_markup', ''), user):
            errors = [i18n('Sorry, there was an internal error.' \
                         + ' The page could not be saved.')]
        else:
            errors = []

        # FIXME: We need more fine-grained control over what is and what isn't outdated.
        self.api.flush_cache(self.api_key)

        # Show.
        html = wiki.get_page_html(alias)
        self.api.render('show.tmpl',
                        may_edit = may_edit,
                        html     = Markup(html),
                        errors   = errors)


    def edit(self, **kwargs):
        wiki     = self.__init_wiki()
        i18n     = self.api.get_i18n()
        may_edit = self.api.get_session().may('edit_content')
        alias    = self.__get_alias()
        name     = self.__get_page_name()

        errors = []
        if not may_edit:
            errors.append(i18n('You are not allowed to edit this page.'))
        elif not wiki.has_page(alias):
            errors.append(i18n('You are editing a new page.'))

        # Show the page.
        content = wiki.get_page_content(alias, kwargs.get('revision'))
        self.api.render('edit.tmpl',
                        name        = name,
                        may_edit    = may_edit,
                        wiki_markup = content,
                        errors      = errors)


    def diff(self, **kwargs):
        wiki     = self.__init_wiki()
        i18n     = self.api.get_i18n()
        may_edit = self.api.get_session().may('edit_content')
        alias    = self.__get_alias()
        name     = self.__get_page_name()

        html = wiki.get_diff_html(alias,
                                  kwargs.get('revision1', 0),
                                  kwargs.get('revision2', 0))
        self.api.render('diff.tmpl',
                        name     = name,
                        may_edit = may_edit,
                        diff     = Markup(html),
                        errors   = errors)


    def history(self, **kwargs):
        wiki     = self.__init_wiki()
        i18n     = self.api.get_i18n()
        may_edit = self.api.get_session().may('edit_content')
        alias    = self.__get_alias()
        name     = self.__get_page_name()
        list     = wiki.get_revision_list(alias, kwargs.get('offset', 0), 20)
        
        # Show the page.
        self.api.render('history.tmpl',
                        name      = name,
                        revisions = list,
                        may_edit  = may_edit,
                        errors    = [])


    def index(self, **kwargs):
        wiki     = self.__init_wiki()
        i18n     = self.api.get_i18n()
        may_edit = self.api.get_session().may('edit_content')
        alias    = self.__get_alias()
        revision = kwargs.get('revision')

        errors = []
        if not wiki.has_page(alias):
            return self.edit(**kwargs)
        elif revision:
            errors.append(self.i18n('Showing old revision %s' % revision))

        # Show the page.
        html = wiki.get_page_html(alias, revision)
        self.api.render('show.tmpl',
                        may_edit = may_edit,
                        html     = Markup(html),
                        errors   = errors)
