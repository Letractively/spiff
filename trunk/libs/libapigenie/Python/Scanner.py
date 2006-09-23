import sys
sys.path.append('..')
sys.path.append('../..')
from DocumentModel import *
from Plex          import *

""" Define Python lexicon """
# Single char definitions.
letter          = Range('AZaz')
digit           = Range('09')
opening_bracket = Str('(')
closing_bracket = Str(')')
colon           = Str(':')
spaces          = Any(" \t\r\n")
operators       = Any('+-*/=<>')
lineterm        = Str("\n") | Eof
escaped_newline = Str('\n')

# Single word definitions.
number          = Rep1(digit)
name            = letter + Rep(letter | digit)
variable        = Rep1(letter | Str('_')) + Rep(letter | digit | Any('_.'))
function_name   = variable
indentation     = Rep(Str(' ')) | Rep(Str("\t"))
multi_comment   = Str('"""') | Str("'''")

# API doc parser.
api_text        = Rep1(Rep(spaces)          \
                     + Rep(indentation)     \
                     + AnyBut('@ \t\r\n')   \
                     + Rep(AnyBut('"\r\n')) \
                     + Eol)
api_arg_type    = Str('@type')        \
                + Rep(spaces)         \
                + variable            \
                + Rep(spaces)         \
                + colon               \
                + api_text
api_arg_param   = Str('@param')       \
                + Rep(spaces)         \
                + variable            \
                + Rep(spaces)         \
                + colon               \
                + api_text
api_rtype       = Str('@rtype')       \
                + Rep(spaces)         \
                + colon               \
                + api_text
api_rvalue      = Str('@return')      \
                + Rep(spaces)         \
                + colon               \
                + api_text

# Function/Method definition related.
arg_separator   = Opt(spaces) + Str(',') + Opt(spaces)
arg_list        = Opt(variable + Rep(arg_separator + variable))
arg_braces      = opening_bracket     \
                + Rep(spaces)         \
                + arg_list            \
                + Rep(spaces)         \
                + closing_bracket
functions       = Str('def')          \
                + Rep(spaces)         \
                + function_name       \
                + Rep(spaces)         \
                + arg_braces          \
                + colon

# Class definition related.
inherit_list    = arg_list
inherit_braces  = arg_braces
classes         = Str('class')        \
                + Rep(spaces)         \
                + name                \
                + Rep(spaces)         \
                + Opt(inherit_braces) \
                + colon

# Other stuff.
comment         = Str('#') + Rep(AnyBut("\n"))
resword         = Str('if', 'then', 'else', 'end', 'return')
blank_line      = indentation + Opt(comment) + lineterm


""" Implement scanner """
class Parser(Scanner):
    def __init__(self, file, filename):
        Scanner.__init__(self, self.lexicon, file, filename)
        self.indentation_stack     = [0]
        self.bracket_nesting_level = 0
        self.begin('indent')

    def open_bracket_action(self, text):
        self.bracket_nesting_level = self.bracket_nesting_level + 1
        return text

    def close_bracket_action(self, text):
        self.bracket_nesting_level = self.bracket_nesting_level - 1
        return text

    def open_multi_comment(self, text):
        if self.bracket_nesting_level == 0:
            self.begin('multi_comment')
            return 'multi_comment'

    def current_level(self):
        return self.indentation_stack[-1]

    def newline_action(self, text):
        if self.bracket_nesting_level == 0:
            self.begin('indent')
            return 'newline'

    def indentation_action(self, text):
        current_level = self.current_level()
        new_level = len(text)
        if new_level > current_level:
            self.indent_to(new_level)
        elif new_level < current_level:
            self.dedent_to(new_level)
        self.begin('')

    def indent_to(self, new_level):
        self.indentation_stack.append(new_level)
        self.produce('INDENT', '')

    def dedent_to(self, new_level):
        while new_level < self.current_level():
            self.indentation_stack.pop()
            self.produce('DEDENT', '')

    def eof(self):
        self.dedent_to(0)

    lexicon = Lexicon([
        # Words.
        (classes,         'class'),
        (functions,       'function'),

        # Braces, dots, operators.
        (opening_bracket, open_bracket_action),
        (closing_bracket, close_bracket_action),

        # Comments.
        (comment,         'comment'),
        (multi_comment,   open_multi_comment),
        State('multi_comment', [
            (multi_comment,   Begin('')),
            (api_arg_type,    'arg_type'),
            (api_arg_param,   'arg_param'),
            (api_rtype,       'return_type'),
            (api_rvalue,      'return_value'),
            (api_text,        'comment_text'),
            (AnyChar,         IGNORE)
        ]),

        # Whitespace / control characters.
        (lineterm,        newline_action),
        State('indent', [
            (blank_line,  IGNORE),
            (indentation, indentation_action),
        ]),
        (AnyChar,         TEXT)
    ])


""" Unit test """
if __name__ == '__main__':
    import unittest
    import re
    from libuseful_python.string import wrap

    class ParserTest(unittest.TestCase):
        def runTest(self):
            filename  = 'testfile.py'
            infile    = open(filename, "r")
            scanner   = Parser(infile, filename)
            while True:
                token    = scanner.read()
                position = scanner.position()
                if token[0] is None: break

    testcase = ParserTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
