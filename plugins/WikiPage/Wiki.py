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
import difflib
import Warehouse
from cgi        import escape
from genshi     import Markup
from WikiMarkup import Wiki2Html
from WikiPage   import WikiPage

class Wiki(object):
    def __init__(self, db, **kwargs):
        self.db                = db
        self.warehouse         = Warehouse.DB(db)
        self.__class__.differ  = difflib.Differ()
        self.__class__.matcher = difflib.SequenceMatcher()
        self.wiki2html         = Wiki2Html()
        if kwargs.has_key('directory'):
            self.warehouse.set_directory(kwargs.get('directory'))
        if kwargs.has_key('wiki_word_handler'):
            self.wiki2html.set_wiki_word_handler(kwargs.get('wiki_word_handler'))
        if kwargs.has_key('wiki_url_handler'):
            self.wiki2html.set_url_handler(kwargs.get('wiki_url_handler'))


    def set_directory(self, directory):
        self.warehouse.set_directory(directory)


    def set_wiki_word_handler(self, handler):
        self.wiki2html.set_wiki_word_handler(handler)


    def set_url_handler(self, handler):
        self.wiki2html.set_url_handler(handler)


    def __markup_diff_line(self, line_from, line_to):
        #print "IN_FROM:", line_from
        #print "IN_TO:  ", line_to
        self.__class__.matcher.set_seq1(line_from)
        self.__class__.matcher.set_seq2(line_to)
        line_from_new = ''
        line_to_new   = ''
        for opcode in self.__class__.matcher.get_opcodes():
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


    def __get_page_item(self, alias, revision = None):
        if revision is not None:
            item = self.warehouse.get_file_from_alias(alias, int(revision))
            if item is not None:
                return item
        return self.warehouse.get_file_from_alias(alias)


    def has_page(self, alias):
        """
        @rtype:  bool
        @return: True if a page with the given alias exists, False otherwise.
        """
        return self.warehouse.get_file_from_alias(alias) is not None


    def get_page(self, alias, revision = None):
        """
        Returns the page with the given alias and the given revision. If a 
        revision was not given, the most recent version is returned.

        @rtype:  WikiPage
        @return: The page with the given alias, ot None if it does not exist.
        """
        item = self.__get_page_item(alias, revision)
        assert item.get_filename() is not None
        assert len(item.get_filename()) > 0
        return WikiPage(self, None, item = item)


    def save_page(self, page):
        """
        Saves the given page in the database.

        @type  page: WikiPage
        @param page: The page to be saved.
        @rtype:  bool
        @return: True on success, False otherwise.
        """
        return self.warehouse.add_file(page.item)


    def get_revision_list(self, alias, offset = 0, limit = 0):
        """
        Returns the list of all revisions of the given page in the
        database. The result may be restricted by the given offset
        and limit.

        @type  alias: string
        @param alias: The alias of the page.
        @type  offset: int
        @param offset: The offset of the first result.
        @type  limit: int
        @param limit: The maximum number of results.
        @rtype:  list[WikiPage]
        @return: A list of wiki pages.
        """
        result = []
        for item in self.warehouse.get_file_list_from_alias(alias,
                                                            True,
                                                            offset,
                                                            limit):
            result.append(WikiPage(self, '', item = item))
        return result


    def get_diff(self, alias, revision1, revision2):
        item1 = self.warehouse.get_file_from_alias(alias, int(revision1))
        item2 = self.warehouse.get_file_from_alias(alias, int(revision2))
        assert item1 is not None
        assert item2 is not None
        content_from = item1.get_content()
        content_to   = item2.get_content()
        return self.__markup_diff(content_from, content_to)
