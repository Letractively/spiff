def mkurl(url, **kwargs):
    """
    Returns a URL with the given attributes.
    """
    # Build the path of the URL.
    if len(kwargs) > 0:
        url += '?'

    # Append attributes, if any.
    for key in kwargs:
        if url[-1] != '&' and url[-1] != '?':
            url += '&'
        url += key + '=' + str(kwargs[key][0])
    return url
