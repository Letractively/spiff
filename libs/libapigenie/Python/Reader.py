from Parser import *
from libuseful_python.string import wrap
import re

class Reader:
    def __init__(self):
        self.debug     = 0
        self.stack     = []
        self.collector = ''


    def __cleanup_whitespace(self, text):
        regexp = re.compile('[ \t]+')
        text   = regexp.sub(' ', text.strip())
        return text


    def __cleanup_linebreaks(self, text):
        regexp = re.compile('(\S[^\n]*)\n')
        text   = regexp.sub('\\1', text)
        regexp = re.compile('[\r\n]\s+')
        text   = regexp.sub('\n', text)
        text   = text.replace('\n', '\n\n')
        return text


    def __collector_flush(self):
        #print "Flushing: >>", self.collector, "<<"
        self.stack[-1].add_child(Chunk(self.collector))
        self.collector = ''


    def store_token(self, token):
        if self.debug > 2:
            print 'Token(%s): %s' % (token[0], token[1])

        if token[0] is 'class':
            self.__collector_flush()
            token_text = self.__cleanup_whitespace(token[1])
            class_def  = token_text[4:]
            class_name = class_def[0:-1]
            my_class   = Class(token[1], class_name)
            self.stack[-1].add_child(my_class)
            self.stack.append(my_class)
            if self.debug > 0:
                print
                print '********** Class:', class_name, '**********'
        elif token[0] is 'function':
            self.__collector_flush()
            token_text = self.__cleanup_whitespace(token[1])
            words      = token_text.split(' ')
            words.pop(0)
            func_name  = words.pop(0)
            arg_string = ''.join(words)
            func       = Function(token[1], func_name)
            self.stack[-1].add_child(func)
            self.stack.append(func)
            if self.debug > 0:
                print '--------------'
                print 'Function:', token[1]
        elif token[0] is 'INDENT_ACTION':
            if self.debug > 0:
                print 'Indenting'
        elif token[0] is 'DEDENT_ACTION':
            if self.debug > 0:
                print 'Dedenting'
            self.__collector_flush()
            self.stack.pop()
        elif token[0] is 'comment_text':
            self.collector += token[1]
            if self.debug > 0:
                print 'Comment:'
                text = wrap(token[1], 50)
                for line in text.split("\n"):
                    print ' ', line
        elif token[0] is 'arg_type':
            self.collector += token[1]
            arg_string = self.__cleanup_whitespace(token[1])
            words      = arg_string.split(' ')
            name       = words[1][0:-1]
            type       = ''.join([s for s in arg_string.split(':')[1:]])
            if self.stack[-1].has_arg(name):
                self.stack[-1].get_arg(name).set_type(type)
            else:
                arg = Variable(name, type)
                self.stack[-1].add_arg(arg)
            if self.debug > 1:
                print 'Argument name:', name, 'Type:', type
        elif token[0] is 'arg_param':
            self.collector += token[1]
            arg_string = self.__cleanup_whitespace(token[1])
            words      = arg_string.split(' ')
            name       = words[1][0:-1]
            docs       = ''.join([s for s in arg_string.split(':')[1:]])
            if not self.stack[-1].has_arg(name):
                arg = Variable(name)
                self.stack[-1].add_arg(arg)
            self.stack[-1].get_arg(name).set_docs(docs)
            if self.debug > 1:
                print 'Argument name:', name, 'Docs:', docs
        elif token[0] is 'return_type':
            self.collector += token[1]
            ret_string = self.__cleanup_whitespace(token[1])
            type       = ''.join([s for s in ret_string.split(':')[1:]])
            ret        = self.stack[-1].get_return()
            if ret:
                ret.set_type(type)
            else:
                ret = Variable('return_value', type)
                self.stack[-1].set_return(ret)
            if self.debug > 1:
                print 'Return type:', token[1]
        elif token[0] is 'return_value':
            self.collector += token[1]
            ret_string = self.__cleanup_whitespace(token[1])
            docs       = ''.join([s for s in ret_string.split(':')[1:]])
            ret        = self.stack[-1].get_return()
            if not ret:
                ret = Variable('return_value')
                self.stack[-1].set_return(ret)
            ret.set_docs(docs)
            if self.debug > 1:
                print 'Return value explanation:', token[1]
        elif token[0] is 'eof':
            self.__collector_flush()
        else:
            # Default is to grab the text into a string chunk.
            if self.debug > 1:
                print 'Text Token(%s): "%s"' % (token[0], token[1])
            self.collector += token[1]


    def read(self, filename):
        infile    = open(filename, 'r')
        parser    = Parser(infile, filename)
        self.file = File(filename)
        self.stack.append(self.file)
        while True:
            token    = parser.read()
            position = parser.position()
            if token[0] is None: break
            self.store_token(token)
        #print self.file.get_string(),
        return True


if __name__ == '__main__':
    import unittest

    class ReaderTest(unittest.TestCase):
        def runTest(self):
            # Read the entire file into one string
            filename = 'testfile.py'
            infile   = open(filename, 'r')
            in_str   = infile.read()
            infile.close()

            # Parse the file.
            reader   = Reader()
            reader.read(filename)
            
            out_str = reader.file.get_string()
            assert len(out_str) > 10
            assert out_str == in_str

    testcase = ReaderTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
