#!/usr/bin/python
try:
    import go
except SystemExit:
    pass
except Exception, e:
    print 'Content-Type: text/html; charset=utf-8'
    print
    raise
