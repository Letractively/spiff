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
import sys
sys.path.append('..')
from Plex import *

# Single char definitions.
letter      = Range('AZaz')
digit       = Range('09')
spaces      = Any(" \t\r\n")
nl          = Str("\n") | Eof
not_nl      = AnyBut("\r\n")
colon       = Str(':')
hash        = Str('#')
equal       = Str('=')
star        = Str('*')
slash       = Str('/')
o_bracket   = Str('{')
c_bracket   = Str('}')
underscore  = Str('_')
punctuation = Any('.!?,;')

# Single word definitions.
name        = letter + Rep(letter | digit)
indentation = Rep(Str(' ')) | Rep(Str("\t"))
variable    = letter + Rep(letter | digit | Str('_')) + Rep(letter | digit)

# Markup.
line          = Rep(not_nl) + nl
blank_line    = indentation + nl
words         = Rep1(letter | digit | spaces)
list_item     = Bol + Alt(hash, star) + Str(' ')
italic_start  = Alt(Bol, spaces) + slash
italic_end    = slash + Alt(Eol, spaces, punctuation)
title1        = equal + words + equal
title2        = equal + equal + words + equal + equal
title3        = equal + equal + equal + words + equal + equal + equal
table         = Str('#Table') + nl
heading       = Str('#Heading') + nl
row           = Str('#Row') + nl
cell          = Rep1(Str('|')) + Str(' ')

class WikiParser(Scanner):
    def __init__(self, file, filename):
        Scanner.__init__(self, self.lexicon, file, filename)
        self.my_buffer             = ''
        self.indentation_stack     = [0]
        self.bracket_nesting_level = 0
        self.in_italic             = False
        self.in_bold               = False
        self.in_underline          = False
        self.in_list               = False
        self.in_list_item          = False
        self.in_table              = False
        self.in_heading            = False
        self.in_row                = False
        self.in_cell               = False
        self.begin('indent')

    def _buffer_flush(self):
        indent = self._get_current_indent_level()
        #print "_buffer_flush (%i): '%s'" % (indent, self.my_buffer)
        if self.my_buffer != '':
            self.produce('text', self.my_buffer)
            self.my_buffer = ''

    def _newline_action(self, text):
        #print '_newline_action'
        self._buffer_flush()
        self.produce('newline', text)
        if self.bracket_nesting_level == 0:
            self.begin('indent')

    def _indentation_action(self, text):
        #print '_indentation_action'
        self.my_buffer += text
        self._buffer_flush()
        current_level = self._get_current_indent_level()
        new_level     = len(text)
        if new_level > current_level:
            self._indent_to(new_level)
        elif new_level < current_level:
            self._dedent_to(new_level)
        self.begin('')

    def _indent_to(self, new_level):
        self.indentation_stack.append(new_level)
        self.produce('indent', new_level)

    def _dedent_to(self, new_level):
        while new_level < self._get_current_indent_level():
            self.indentation_stack.pop()
        self.produce('dedent', self._get_current_indent_level())

    def _get_current_indent_level(self):
        return self.indentation_stack[-1]

    def _title1(self, text):
        #print '_title1: ' + text
        self._buffer_flush()
        self.produce('title1_start', text[0])
        self.my_buffer += text[1:-1]
        self._buffer_flush()
        self.produce('title1_end', text[-1])

    def _title2(self, text):
        #print '_title2: ' + text
        self._buffer_flush()
        self.produce('title2_start', text[0:2])
        self.my_buffer += text[2:-2]
        self._buffer_flush()
        self.produce('title2_end', text[-2:])

    def _title3(self, text):
        #print '_title3: ' + text
        self._buffer_flush()
        self.produce('title3_start', text[0:3])
        self.my_buffer += text[3:-3]
        self._buffer_flush()
        self.produce('title3_end', text[-3:])

    def _italic_start(self, text):
        #print '_italic_start'
        self.my_buffer += text[0]
        self._buffer_flush()
        self.in_italic = True
        self.produce('italic_start', text[1])

    def _italic_end(self, text):
        #print '_italic_end'
        self._buffer_flush()
        self.produce('italic_end', text[0])
        self.in_italic = False
        self.my_buffer += text[1]

    def _bold(self, text):
        #print '_bold'
        self._buffer_flush()
        if self.in_bold:
            self.produce('bold_end', text)
            self.in_bold = False
        else:
            self.in_bold = True
            self.produce('bold_start', text)

    def _underline(self, text):
        #print '_underline'
        self._buffer_flush()
        if self.in_underline:
            self.produce('underline_end', text)
            self.in_underline = False
        else:
            self.in_underline = True
            self.produce('underline_start', text)

    def _list_item(self, text):
        self._buffer_flush()
        if not self.in_list:
            if text.startswith('#'):
                self.produce('numbered_list_start', '')
            elif text.startswith('*'):
                self.produce('unnumbered_list_start', '')
            self.in_list = True
        if self.in_list_item:
            self._list_item_end()
        self.in_list_item = True
        self.produce('list_item_start')
    
    def _list_item_end(self):
        self.in_list_item = False
        self.produce('list_item_end', '')

    def _list_end(self):
        if self.in_list_item:
            self._list_item_end()
        self.in_list = False
        self.produce('list_end', '')

    def _table_start(self, text):
        self._buffer_flush()
        self.produce('table_start', text[:-1])
        self._newline_action(text[-1])
        self.in_table   = True

    def _heading_start(self, text):
        self._buffer_flush()
        if not self.in_table:
            self._text(text)
            return
        if self.in_heading:
            self._heading_end()
        self.in_heading = True
        self.produce('heading_start', text[:-1])
        self._newline_action(text[-1])

    def _row_start(self, text):
        self._buffer_flush()
        if not self.in_table:
            self._text(text)
            return
        if self.in_heading:
            self._heading_end()
        if self.in_row:
            self._row_end()
        self.in_row = True
        self.produce('row_start', text[:-1])
        self._newline_action(text[-1])

    def _cell_start(self, text):
        self._buffer_flush()
        if not self.in_heading and not self.in_row:
            self._text(text)
            return
        if self.in_cell:
            self._cell_end()
        self.in_cell = True
        self.produce('cell_start')

    def _cell_end(self):
        self.in_cell = False
        self.produce('cell_end', '')

    def _row_end(self):
        if self.in_cell:
            self._cell_end()
        self.in_row = False
        self.produce('row_end', '')

    def _heading_end(self):
        if self.in_cell:
            self._cell_end()
        self.in_heading = False
        self.produce('heading_end', '')

    def _table_end(self):
        if self.in_heading:
            self._heading_end()
        if self.in_row:
            self._row_end()
        self.in_table = False
        self.produce('table_end', '')

    def _open_bracket_action(self, text):
        #print '_open_bracket_action'
        self.my_buffer += text
        self.bracket_nesting_level = self.bracket_nesting_level + 1

    def _close_bracket_action(self, text):
        #print '_close_bracket_action'
        self.my_buffer += text
        self.bracket_nesting_level = self.bracket_nesting_level - 1

    def _blank_line(self, text):
        self._dedent_to(0)
        self.my_buffer += text
        if self.in_list:
            self._list_end()
        if self.in_table:
            self._table_end()
        self._buffer_flush()

    def _text(self, text):
        #print "Char: '%s'" % text
        self.my_buffer += text

    def eof(self):
        self._blank_line('')

    lexicon = Lexicon([
        # Handle whitespace and indentation.
        (nl, _newline_action),
        State('indent', [
            (blank_line,  _blank_line),
            (indentation, _indentation_action)
        ]),
        
        # Brackets.
        (o_bracket, _open_bracket_action),
        (c_bracket, _close_bracket_action),

        # Styles.
        (list_item,    _list_item),
        (title1,       _title1),
        (title2,       _title2),
        (title3,       _title3),
        (star,         _bold),
        (underscore,   _underline),
        (italic_start, _italic_start),
        (italic_end,   _italic_end),

        # Tables.
        (table,   _table_start),
        (heading, _heading_start),
        (row,     _row_start),
        (cell,    _cell_start),

        # Other.
        (AnyChar, _text)
    ])


if __name__ == '__main__':
    import unittest

    class ParserTest(unittest.TestCase):
        def runTest(self):
            # Read the entire file into one string.
            filename  = 'markup.txt'
            infile    = open(filename, "r")
            in_text   = infile.read()
            infile.close()

            # Re-open and parse the entire file.
            infile  = open(filename, "r")
            scanner = WikiParser(infile, filename)
            content = ''
            while True:
                token    = scanner.read()
                position = scanner.position()
                if token[0] is None: break
                #print "Token type: %s, Token: '%s'" % (token[0], token[1])
                if not token[0] in ['indent', 'dedent']:
                    content += token[1]

            # Make sure that every single string was extracted.
            #print content
            assert content == in_text

    testcase = ParserTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
