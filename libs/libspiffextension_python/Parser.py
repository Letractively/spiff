import re

# Pre-compile regular expressions.
header_fields = [
    'extension',
    'handle',
    'version',
    'author',
    'description',
    'runtime_dependency',
    'install_time_dependency']
header_end = re.compile('^\s*\*\/$')
line_notag = re.compile('^\s+(.*)$',       re.S)
line_tag   = re.compile('^(\S+):\s+(.+)$', re.S)

# Given the filename of an extension file, this function reads the file and
# parses the comment that is embedded in the header.
# Returns: A map, with each key pointing to either a string, or to a list of
# strings.
def parse_header(filename):
    assert os.path.is_file(filename)
    file = open(file, 'r')

    # Skip first two lines.
    file.readline()
    file.readline()

    # Walk through the header lines.
    header   = {}
    last_tag = ''
    for line in file:
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
        assert last_tag in header_fields
        header[last_tag] = match.group(2)

    # Make sure that the header is complete.
    for field in header_fields:
        # Skip optional fields.
        if field == 'install_time_dependency':
            continue
        assert header.has_key(field)

    # Split the dependencies into a list.
    list = header['runtime_dependency'].split(' ')
    header['runtime_dependency'] = list
    if header.has_key('install_time_dependency'):
        list = header['install_time_dependency'].split(' ')
    header['install_time_dependency'] = list
    return header
