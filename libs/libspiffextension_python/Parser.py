import sys
import os.path
import re

# Define vocabulary.
required_fields = [
    'extension',
    'handle',
    'version',
    'author',
    'author-email',
    'description',
    'runtime_dependency' ]
optional_fields = ['install_time_dependency']

# Pre-compile regular expressions.
header_start = re.compile('^\s*"""$')
header_end   = header_start
line_notag   = re.compile('^\s+(.*)$',       re.S)
line_tag     = re.compile('^(\S+):\s+(.+)$')

# Given the filename of an extension file, this function reads the file and
# parses the comment that is embedded in the header.
# Returns: A map, with each key pointing to either a string, or to a list of
# strings.
def parse_header(filename):
    assert os.path.isfile(filename)
    file = open(filename, 'r')

    # Walk through the header lines.
    in_header = False
    header    = {}
    last_tag  = ''
    for line in file:
        # Find the opening tag of the header.
        if not in_header:
            if header_start.match(line):
                in_header = True
            continue

        # Find a closing tag of the header.
        if header_end.match(line):
            break
        
        # Parse a line that contains a string, but no field name.
        match = line_notag.match(line)
        if match is not None:
            assert last_tag is not None
            assert header.has_key(last_tag)
            header[last_tag] += match.group(1)
            continue

        # Parse a line that contains a field name.
        match = line_tag.match(line)
        if match is None:
            continue

        # Make sure that the extracted tag is valid.
        last_tag = match.group(1).lower()
        assert last_tag in required_fields or last_tag in optional_fields
        header[last_tag] = match.group(2)

    # Make sure that the header is complete.
    for field in required_fields:
        assert header.has_key(field)

    # Split the dependencies into a list.
    list = header['runtime_dependency'].split(' ')
    header['runtime_dependency'] = list
    if header.has_key('install_time_dependency'):
        list = header['install_time_dependency'].split(' ')
    header['install_time_dependency'] = list
    return header


if __name__ == '__main__':
    import unittest

    class ParserTest(unittest.TestCase):
        def runTest(self):
            filename = 'HelloWorldExtension.py'
            header   = parse_header(filename)
            assert header is not None
            assert len(header) == 8
            #for field in required_fields:
            #    print field + ':', header[field]

    testcase = ParserTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
