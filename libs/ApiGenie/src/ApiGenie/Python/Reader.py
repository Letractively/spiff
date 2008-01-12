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
from DocumentModel import Chunk
from Parser        import Parser
from my_string     import *
import PyDocString
import StringIO

class Reader(object):
    def __init__(self):
        self.debug     = 0
        self.stack     = []


    def _add_class(self, token):
        token_text = cleanup_whitespace(token[1])
        class_def  = token_text[6:]
        class_name = class_def[0:-1]
        my_class   = Chunk(token[0], token[1], class_name)
        self.stack[-1].add_child(my_class)
        self.stack.append(my_class)
        if self.debug > 0:
            print '** Class:', class_name, '**'

    def _add_function(self, token):
        token_text = cleanup_whitespace(token[1])
        func_def   = token_text[4:]
        words      = func_def.split('(')
        func_name  = words.pop(0)
        arg_string = ''.join(words)[0:-1]
        func       = Chunk(token[0], token[1], func_name)
        self.stack[-1].add_child(func)
        self.stack.append(func)
        if self.debug > 0:
            print 'Function:', func_name

    def _add_documentation(self, token):
        text   = StringIO.StringIO(token[1])
        parser = PyDocString.Parser(text, '')
        while True:
            token = parser.read()
            if token[0] is None: break
            assert False # Parser should not produce anything.
        chunk = parser.apidoc
        text.close()
        self.stack[-1].add_child(chunk)
        if self.debug > 0:
            print 'Documentation:'
            text = wrap(token[1], 50)
            for line in text.split("\n"):
                print ' ', line

    def _add_chunk(self, token):
        if self.debug > 2:
            print 'Token(%s): %s' % (token[0], token[1])

        if token[0] is 'class':
            self._add_class(token)
        elif token[0] is 'function':
            self._add_function(token)
        elif token[0] is 'DEDENT_ACTION':
            self.stack.pop()
        elif token[0] is 'multi_line_comment' \
             and self.stack[-1].get_n_children('documentation') == 0:
            self._add_documentation(token)
        else:
            chunk = Chunk(token[0], token[1], '')
            self.stack[-1].add_child(chunk)


    def read(self, filename):
        infile = open(filename, 'r')
        parser = Parser(infile, filename)
        file   = Chunk('file', '', filename)
        self.stack.append(file)
        while True:
            token    = parser.read()
            position = parser.position()
            if token[0] is None: break
            self._add_chunk(token)
        infile.close()
        return file


if __name__ == '__main__':
    import unittest

    class ReaderTest(unittest.TestCase):
        def runTest(self):
            # Read the entire file into one string.
            filename = 'testfile.py'
            infile   = open(filename, 'r')
            in_str   = infile.read()
            infile.close()

            # Parse the file.
            reader = Reader()
            file   = reader.read(filename)
            
            # Make sure that the model is complete.
            out_str = file.get_data()
            assert len(out_str) > 10
            assert out_str == in_str

    testcase = ReaderTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
