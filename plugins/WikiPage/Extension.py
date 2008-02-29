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
from cgi    import escape
from string import split
from genshi import Markup

class Extension:
    def __init__(self, api):
        self.api               = api
        self.i18n              = api.get_i18n()
        self.db                = api.get_db()
        self.page              = api.get_session().get_requested_page()
        self.wiki2html         = None
        self.warehouse         = None
        self.warehouse_mod     = None
        self.__class__.differ  = None
        self.__class__.matcher = None


    def __init_wiki(self):
        if self.wiki2html is not None:
            return
        difflib = __import__('difflib',
                             globals(),
                             locals(),
                             'difflib')
        self.__class__.differ  = difflib.Differ()
        self.__class__.matcher = difflib.SequenceMatcher()

        module = __import__('WikiMarkup.Wiki2Html',
                            globals(),
                            locals(),
                            'Wiki2Html')
        self.wiki2html = module.Wiki2Html()
        self.wiki2html.set_wiki_word_handler(self.__wiki_word_handler)
        self.wiki2html.set_url_handler(self.__wiki_url_handler)

        self.warehouse_mod = __import__('Warehouse.DB',
                                        globals(),
                                        locals(),
                                        'DB')
        data_directory = os.path.join(self.api.get_data_dir(), 'warehouse')
        self.warehouse = self.warehouse_mod.DB(self.db)
        self.warehouse.set_directory(data_directory)


    def __wiki_word_handler(self, url, word):
        alias  = self.api.get_get_data('page')
        # The user is viewing the homepage of his web presence.
        if alias is None:
            url = self.api.get_requested_uri(page = [word], revision = None)
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
        url = self.api.get_requested_uri(page = ['/'.join(stack)], revision = None)
        return (url, word)


    def __wiki_url_handler(self, url, word):
        if url.find(':') == -1:
            url = self.api.get_requested_uri(page = [url], revision = None)
        return (url, word)


    def __markup_diff_line(self, line_from, line_to):
        #print "IN_FROM:", line_from
        #print "IN_TO:  ", line_to
        sequence_matcher.set_seq1(line_from)
        sequence_matcher.set_seq2(line_to)
        line_from_new = ''
        line_to_new   = ''
        for opcode in sequence_matcher.get_opcodes():
            if opcode[0] == 'equal':
                line_from_new += escape(line_from[opcode[1]:opcode[2]])
                line_to_new   += escape(line_to[opcode[3]:opcode[4]])
            elif opcode[0] == 'replace':
                line_from_new += '<span class="diff_replace">'
                line_to_new   += '<span class="diff_replace">'
                line_from_new += escape(line_from[opcode[1]:opcode[2]])
                line_to_new   += escape(line_to[opcode[3]:opcode[4]])
                line_from_new += '</span>'
                line_to_new   += '</span>'
            elif opcode[0] == 'delete':
                line_from_new += '<span class="diff_delete">'
                line_from_new += escape(line_from[opcode[1]:opcode[2]])
                line_from_new += '</span>'
            elif opcode[0] == 'insert':
                line_to_new += '<span class="diff_insert">'
                line_to_new += escape(line_to[opcode[3]:opcode[4]])
                line_to_new += '</span>'
            else:
                print opcode[0]
                assert False # Unknown opcode in diff.
        return (line_from_new, line_to_new)


    def __markup_diff_block(self, deleted, inserted):
        #print "__markup_diff_block():", len(deleted), len(inserted)
        if len(deleted) == 1 and len(inserted) == 1:
            result = self.__markup_diff_line(deleted[0], inserted[0])
            return ([Markup(unicode(result[0], 'utf-8'))],
                    [Markup(unicode(result[1], 'utf-8'))])
        deleted_new  = []
        inserted_new = []
        for line in deleted:
            deleted_line  = '<span class="diff_line_delete">'
            deleted_line += escape(line)
            deleted_line += '</span>'
            deleted_new.append(Markup(unicode(deleted_line, 'utf-8')))
        for line in inserted:
            inserted_line  = '<span class="diff_line_insert">'
            inserted_line += escape(line)
            inserted_line += '</span>'
            inserted_new.append(Markup(unicode(inserted_line, 'utf-8')))
        return (deleted_new, inserted_new)


    def __markup_diff(self, content_from, content_to):
        # Start by comparing line wise.
        lines = self.__class__.differ.compare(content_from.splitlines(1),
                                              content_to.splitlines(1))

        # Now compare the lines in more details.
        diff          = []
        deleted       = []
        inserted      = []
        line_number   = 0
        last_operator = None
        for line in lines:
            operator = line[0]
            if line[-1] == '\n':
                line = line[2:-1]
            else:
                line = line[2:]

            # That's junk we don't care about.
            if operator == '?':
                continue

            # Count the line number in the "from" content.
            elif operator == ' ' or operator == '-':
                line_number += 1

            # Collect all lines of the current block of '+' and '-' lines.
            if operator == '+':
                inserted.append(line)

            # Lines that are equal need not be examined any further.
            elif operator == ' ':
                line = Markup(unicode(line, 'utf-8'))
                diff.append((line_number, 'equal', [line], [line]))

            # When a block is complete, pass it to the diff function about.
            if (len(deleted) + len(inserted) > 0
                and (operator == '+' or operator == ' '
                     or (operator == '-' and last_operator == '-'))):
                (block1, block2) = self.__markup_diff_block(deleted, inserted)

                # Determine the type of change that this block makes.
                if len(block1) == 0:
                    type = 'insert'
                elif len(block2) == 0:
                    type = 'delete'
                elif len(block1) > 0 and len(block2) > 0:
                    type = 'replace'
                
                # Store both blocks in the diff.
                diff.append((line_number, type, block1, block2))
                deleted  = []
                inserted = []
            last_operator = operator

            if operator == '-':
                deleted.append(line)

        # We still need to clear the buffer containing the current block.
        (block1, block2) = self.__markup_diff_block(deleted, inserted)
        if len(block1) == 0:
            type = 'insert'
        elif len(block2) == 0:
            type = 'delete'
        elif len(block1) > 0 and len(block2) > 0:
            type = 'replace'
        if len(block1) != 0 or len(block2) != 0:
            diff.append((line_number, type, block1, block2))
        return diff


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
        current_user = self.api.get_session().get_user()
        if current_user is not None:
            user_name = current_user.get_handle()
        else:
            user_name = os.environ["REMOTE_ADDR"]

        # Copy the data into a warehouse item.
        item = self.warehouse_mod.Item(alias)
        item.set_content(wiki_markup)
        item.set_attribute(user_name = user_name)
        if not self.warehouse.add_file(item):
            msg = i18n('File could not be saved - please contact the author!')
            return (None, [msg])

        # FIXME: We need more fine-grained control over what is and what isn't outdated.
        self.api.flush_cache()
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


    def __show_diff(self, alias, may_edit):
        errors = []
        revision1 = self.api.get_post_data('revision1')
        revision2 = self.api.get_post_data('revision2')
        assert revision1 is not None
        assert revision2 is not None
        item1 = self.warehouse.get_file_from_alias(alias, int(revision1))
        item2 = self.warehouse.get_file_from_alias(alias, int(revision2))
        assert item1 is not None
        assert item2 is not None
        content_from = item1.get_content()
        content_to   = item2.get_content()
        diff         = self.__markup_diff(content_from, content_to)
        
        # Determine the page name.
        if self.api.get_get_data('page') is None and self.page is not None:
            page_name = self.page.get_name()
        else:
            page_name = split(alias, '/')[-1]

        # Show the page.
        tmpl_args = {
            'name':      page_name,
            'diff':      diff,
            'may_edit':  may_edit,
            'errors':    errors
        }
        self.api.render('diff.tmpl', **tmpl_args)


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
            'html':     Markup(unicode(self.wiki2html.html, 'utf-8')),
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
        if item is not None:
            tmpl_args['wiki_markup'] = unicode(item.get_content(), 'utf-8')

        # Show the editor.
        self.api.render('edit.tmpl', **tmpl_args)


    def on_spiff_page_open(self, args):
        save = self.api.get_post_data('save')
        if save is not None:
            self.api.flush_cache()


    def on_render_request(self):
        errors = []
        self.__init_wiki()

        # Collect data.
        edit     = self.api.get_get_data('edit')
        save     = self.api.get_post_data('save')
        history  = self.api.get_get_data('history')
        diff     = self.api.get_post_data('diff')
        revision = self.api.get_get_data('revision')
        handle   = self.page is not None and self.page.get_handle()
        alias    = self.api.get_get_data('page') or handle
        may_edit = self.api.get_session().may('edit_content')
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
        elif diff is not None:
            self.__show_diff(alias, may_edit)
        elif edit is not None or item is None:
            self.__show_editor(item, alias, may_edit)
        else:
            self.__show_page(item, may_edit)
