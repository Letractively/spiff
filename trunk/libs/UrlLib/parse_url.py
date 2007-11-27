import re
from urlparse    import urlparse, urlsplit
from parse_query import parse_query

def parse_url(url, default_protocol = 'http'):
    protocol = default_protocol
    username = None
    password = None
    query    = ''
    if url.find('?') >= 0:
        url, query = url.split('?')
    #print "STEP1:", url
    if url.count('://') > 0:
        protocol, url = url.split('://')
    if url.find('@') >= 0:
        url, hostname = url.split('@')
        #print "STEP2:", (url, hostname)
        if url.count(':') == 2:
            tokens = url.split(':')
            protocol = tokens[0]
            username = tokens[1]
            password = tokens[2]
            #print "STEP3:", protocol, username, password
        elif url.count(':') == 1:
            username, password = url.split(':')
            #print "STEP4:", url
        else:
            username = url
            #print "STEP5:", username
    else:
        if url.count(':') == 1:
            protocol, hostname = url.split(':')
            #print "STEP6:", protocol, hostname
        else:
            hostname = url
            #print "STEP7:", hostname
    #print "RESULT:", (protocol, username, password, hostname, query)
    return protocol, username, password, hostname, parse_query(query)
