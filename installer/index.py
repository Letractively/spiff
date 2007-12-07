#!/usr/bin/python
try:
    import install
except SystemExit:
    pass
except Exception, e:
    print 'Content-Type: text/html; charset=utf-8'
    print
    raise
