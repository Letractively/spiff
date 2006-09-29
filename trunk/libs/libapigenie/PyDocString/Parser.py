import sys
sys.path.append('..')
sys.path.append('../..')
from Generator     import Generator
from DocumentModel import *
from my_string     import *
from Plex          import *
import re

# Single char definitions.
letter    = Range('AZaz')
digit     = Range('09')
spaces    = Any(" \t\r\n")
nl        = Str("\n") | Eof
not_nl    = AnyBut("\r\n")
colon     = Str(':')

# Single word definitions.
variable    = Rep1(letter | Str('_')) + Rep(letter | digit | Any('_.'))
indentation = Rep1(Str(' ') | Str("\t"))
doc_delim   = Str('"""') | Str("'''")

# API doc parser.
text         = Rep1(Rep(indentation)     \
                  + AnyBut('@ \t\r\n')   \
                  + Rep1(not_nl)         \
                  + Rep1(nl))
arg_type     = Str('@type')        \
             + Rep(spaces)         \
             + variable            \
             + Rep(spaces)         \
             + colon               \
             + text
arg_param    = Str('@param')       \
             + Rep(spaces)         \
             + variable            \
             + Rep(spaces)         \
             + colon               \
             + text
return_type  = Str('@rtype')       \
             + Rep(spaces)         \
             + colon               \
             + text
return_param = Str('@return')      \
             + Rep(spaces)         \
             + colon               \
             + text

class Parser(Scanner):
    arg_modifier_re    = re.compile('^@(\w+)\s+(\w+)\s*:\s*(.*)[\r\n]$', re.S)
    return_modifier_re = re.compile('^@(\w+)\s*:\s*(.*)[\r\n]$',         re.S)

    def __init__(self, file, filename):
        Scanner.__init__(self, self.lexicon, file, filename)
        self.apidoc = ApiDoc('', Generator())

    def _newline_action(self, text):
        #print '_newline_action'
        self.apidoc.data += text

    def _description(self, text):
        #print "_description:", text
        self.apidoc.data += text
        text = cleanup_whitespace(text)
        text = cleanup_linebreaks(text)
        self.apidoc.set_description(text)

    def _arg_type(self, text):
        #print "_arg_type:", text
        self.apidoc.data += text
        arg_name = self.arg_modifier_re.sub('\\2', text)
        arg_type = self.arg_modifier_re.sub('\\3', text)
        arg_type = cleanup_whitespace(arg_type)
        arg_type = cleanup_linebreaks(arg_type)
        arg      = self.apidoc.get_argument(arg_name)
        if arg:
            arg.set_type(arg_type)
        else:
            arg = Variable(arg_name, arg_type)
            self.apidoc.add_argument(arg)

    def _arg_param(self, text):
        #print "_arg_param: '%s'" % text
        self.apidoc.data += text
        arg_name  = self.arg_modifier_re.sub('\\2', text)
        arg_param = self.arg_modifier_re.sub('\\3', text)
        arg_param = cleanup_whitespace(arg_param)
        arg_param = cleanup_linebreaks(arg_param)
        arg       = self.apidoc.get_argument(arg_name)
        if not arg:
            arg = Variable(arg_name, '')
            self.apidoc.add_argument(arg)
        arg.set_docs(arg_param)

    def _return_type(self, text):
        #print "_return_type:", text
        self.apidoc.data += text
        return_type = self.return_modifier_re.sub('\\2', text)
        return_type = cleanup_whitespace(return_type)
        return_type = cleanup_linebreaks(return_type)
        return_var  = self.apidoc.get_return()
        if return_var:
            return_var.set_type(return_type)
        else:
            return_var = Variable('return', return_type)
            self.apidoc.set_return(return_var)

    def _return_param(self, text):
        #print "_return_param:", text
        self.apidoc.data += text
        return_param = self.return_modifier_re.sub('\\2', text)
        return_param = cleanup_whitespace(return_param)
        return_param = cleanup_linebreaks(return_param)
        return_var   = self.apidoc.get_return()
        if not return_var:
            return_var = Variable('return', '')
            self.apidoc.set_return(return_var)
        return_var.set_docs(return_param)

    def _indent(self, text):
        #print "_indent: '%s'" % text
        self.apidoc.data += text

    def _sink(self, text):
        #print "_sink: '%s'" % text
        assert False # Unknown character

    def eof(self):
        self.apidoc.mark_unmodified()

    lexicon = Lexicon([
        (text,          _description),
        (arg_type,      _arg_type),
        (arg_param,     _arg_param),
        (return_type,   _return_type),
        (return_param,  _return_param),
        (nl,            _newline_action),
        (indentation,   _indent)
    ])


if __name__ == '__main__':
    import unittest

    class ParserTest(unittest.TestCase):
        def runTest(self):
            # Read the entire file into one string.
            filename  = 'testfile1.docstring'
            infile    = open(filename, "r")
            in_text   = infile.read()
            infile.close()

            # Re-open and parse the entire file.
            infile  = open(filename, "r")
            scanner = Parser(infile, filename)
            while True:
                token    = scanner.read()
                position = scanner.position()
                if token[0] is None: break
                assert False # This scanner produces no strings.

            # Make sure that every single string was extracted.
            content = scanner.apidoc.get_data()
            assert content == in_text

    testcase = ParserTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
