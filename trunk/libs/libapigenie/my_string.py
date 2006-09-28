import re

def wrap(text, width):
    """
    A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\n).
    """
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line)-line.rfind('\n')-1
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )


def cleanup_whitespace(text):
    regexp = re.compile('[ \t]+')
    text   = regexp.sub(' ', text.strip())
    return text


def cleanup_linebreaks(text):
    regexp = re.compile('(\S[^\n]*)\n')
    text   = regexp.sub('\\1', text)
    regexp = re.compile('[\r\n]\s+')
    text   = regexp.sub('\n', text)
    text   = text.replace('\n', '\n\n')
    return text
