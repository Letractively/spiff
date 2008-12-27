from unquote import unquote

def parse_query(query, keep_blank_values=0, strict_parsing=0):
    """Parse a URL query string and return the components as a dictionary.

    Based on the cgi.parse_qs method. This is a utility function provided
    by urlparse so that users need not use the cgi module for
    parsing the url query string.

        Arguments:

        url: URL with query string to be parsed

        keep_blank_values: flag indicating whether blank values in
            URL encoded queries should be treated as blank strings.
            A true value indicates that blanks should be retained as
            blank strings.  The default false value indicates that
            blank values are to be ignored and treated as if they were
            not included.

        strict_parsing: flag indicating what to do with parsing errors.
            If false (the default), errors are silently ignored.
            If true, errors raise a ValueError exception.
    """

    pairs = [s2 for s1 in query.split('&') for s2 in s1.split(';')]
    query = []
    for name_value in pairs:
        if not name_value and not strict_parsing:
            continue
        nv = name_value.split('=', 1)
        if len(nv) != 2:
            if strict_parsing:
                raise ValueError, "bad query field: %r" % (name_value,)
            # Handle case of a control-name with no equal sign
            if keep_blank_values:
                nv.append('')
            else:
                continue
        if len(nv[1]) or keep_blank_values:
            name = unquote(nv[0].replace('+', ' '))
            value = unquote(nv[1].replace('+', ' '))
            query.append((name, value))

    dict = {}
    for name, value in query:
        if name in dict:
            dict[name].append(value)
        else:
            dict[name] = [value]
    return dict
