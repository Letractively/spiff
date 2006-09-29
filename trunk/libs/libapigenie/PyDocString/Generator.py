import sys
sys.path.append('..')
import re
from   my_string import *

class Generator:
    def __init__(self):
        self.type = 'Python DocString'

    def get_type(self):
        """
        Returns a human readable name of the type of API documentation
        that this generator produces.
        """
        return self.type

    def _find_indent(self, text):
        regexp     = re.compile('[\r\n]?(\s+)')
        whitespace = regexp.match(text).group(1)
        return whitespace
        
    def _indent(self, indent, text):
        output = ''
        for line in text.split("\n"):
            output += indent + line + "\n"
        return output
        
    def get_data(self, api_doc_chunk):
        indent   = self._find_indent(api_doc_chunk.data)
        wrap_pos = 79 - len(indent)

        # Build the introduction, if any.
        introduction = api_doc_chunk.get_introduction()
        if introduction != '':
            introduction = wrap(introduction, wrap_pos)
            output       = introduction + "\n\n"
        else:
            output       = ''
        
        # Build the description.
        description = api_doc_chunk.get_description()
        if description != '':
            description  = wrap(description, wrap_pos)
            output      += description + "\n\n"

        # Argument list.
        for arg in api_doc_chunk.get_argument_list():
            if arg.get_name() == '':
                continue
            type  = '@type  ' + arg.get_name() + ': ' + arg.get_type() + "\n"
            param = '@param ' + arg.get_name() + ': ' + arg.get_docs() + "\n"
            output += wrap(type,  wrap_pos)
            output += wrap(param, wrap_pos)
        
        # Return value.
        return_var = api_doc_chunk.get_return()
        if return_var is not None:
            type  = '@rtype:  ' + return_var.get_type() + "\n"
            param = '@return: ' + return_var.get_docs() + "\n"
            output += wrap(type,  wrap_pos)
            output += wrap(param, wrap_pos)
        return self._indent(indent, output.strip())
