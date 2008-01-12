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
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from Plex import *

# Single char definitions.
letter    = Range('AZaz')
digit     = Range('09')
spaces    = Any(" \t\r\n")
nl        = Str("\n") | Eof
not_nl    = AnyBut("\r\n")
o_bracket = Str('(')
c_bracket = Str(')')
colon     = Str(':')

# Single word definitions.
name        = letter + Rep(letter | digit)
indentation = Rep(Str(' ')) | Rep(Str("\t"))
variable    = Rep1(letter | Str('_')) + Rep(letter | digit | Any('_.'))
func_name   = variable
module      = variable + Rep(Str('.') + variable)

# Function/Method definition related.
arg_separator   = Rep(spaces) + Str(',') + Rep(spaces)
arg_list        = Opt(variable + Rep(arg_separator + variable))
arg_braces      = o_bracket           \
                + Rep(spaces)         \
                + arg_list            \
                + Rep(spaces)         \
                + c_bracket
functions       = Str('def')          \
                + Rep1(spaces)        \
                + func_name           \
                + Rep(spaces)         \
                + arg_braces          \
                + colon

# Class definition related.
inherit_braces  = arg_braces
classes         = Str('class')        \
                + Rep(spaces)         \
                + name                \
                + Rep(spaces)         \
                + Opt(inherit_braces) \
                + colon

# Keywords.
kw_import      = Str('import') + Rep1(spaces) + module
kw_from_import = Str('from')          \
               + Rep1(spaces)         \
               + module               \
               + Rep1(spaces)         \
               + Str('import')        \
               + Rep1(spaces)         \
               + (name | Str('*'))
kw_return      = Str('return') + Rep1(spaces) + Rep1(not_nl)

# Other definitions.
line                = Rep(not_nl) + nl
blank_line          = indentation + nl
comment             = Str('#') + Rep(not_nl)
multi_comment_delim = Str('"""') | Str("'''")

class Parser(Scanner):
    def __init__(self, file, filename):
        Scanner.__init__(self, self.lexicon, file, filename)
        self.my_buffer             = ''
        self.indentation_stack     = [0]
        self.bracket_nesting_level = 0
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

    def _dedent_to(self, new_level):
        while new_level < self._get_current_indent_level():
            self.indentation_stack.pop()
            self.produce('DEDENT_ACTION', '')

    def _get_current_indent_level(self):
        return self.indentation_stack[-1]

    def _open_multi_line_comment(self, text):
        #print '_open_multi_line_comment'
        self._buffer_flush()
        self.produce('documentation_delimiter', text)
        self.begin('multi_comment')

    def _close_multi_line_comment(self, text):
        #print '_close_multi_line_comment'
        self.produce('multi_line_comment', self.my_buffer)
        self.my_buffer = ''
        self.produce('documentation_delimiter', text)
        self.begin('')

    def _open_bracket_action(self, text):
        #print '_open_bracket_action'
        self.my_buffer += text
        self.bracket_nesting_level = self.bracket_nesting_level + 1

    def _close_bracket_action(self, text):
        #print '_close_bracket_action'
        self.my_buffer += text
        self.bracket_nesting_level = self.bracket_nesting_level - 1

    def _text(self, text):
        #print "Char:", text
        self.my_buffer += text

    def eof(self):
        self._dedent_to(0)
        pass

    lexicon = Lexicon([
        # Handle whitespace and indentation.
        (nl, _newline_action),
        State('indent', [
            (blank_line,  _text),
            (indentation, _indentation_action)
        ]),
        
        (multi_comment_delim, _open_multi_line_comment),
        State('multi_comment', [
            (multi_comment_delim, _close_multi_line_comment),
            (AnyChar,             _text)
        ]),

        # Brackets.
        (o_bracket, _open_bracket_action),
        (c_bracket, _close_bracket_action),

        # Keywords.
        (kw_import,      'import'),
        (kw_from_import, 'from_import'),
        (kw_return,      'return'),
        (classes,        'class'),
        (functions,      'function'),

        # Other.
        (comment,       'comment'),
        (AnyChar,       _text),
    ])


if __name__ == '__main__':
    import unittest

    class ParserTest(unittest.TestCase):
        def runTest(self):
            # Read the entire file into one string.
            filename  = 'testfile.py'
            infile    = open(filename, "r")
            in_text   = infile.read()
            infile.close()

            # Re-open and parse the entire file.
            infile  = open(filename, "r")
            scanner = Parser(infile, filename)
            content = ''
            while True:
                token    = scanner.read()
                position = scanner.position()
                if token[0] is None: break
                #print "Token type: %s, Token: '%s'" % (token[0], token[1])
                content += token[1]

            # Make sure that every single string was extracted.
            assert content == in_text

    testcase = ParserTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
