#!/usr/bin/python
import os, os.path
os.chdir(os.path.dirname(__file__))
try:
    import install
    if __name__ == '__main__':
        from UrlLib import CgiRequest
        request = CgiRequest()
        install.run(request)
        request.flush()
except Exception, e:
    print 'Content-Type: text/plain; charset=utf-8'
    print
    import traceback, sys
    traceback.print_exc(file=sys.stdout)
    sys.exit(1)

def index(req):
    from UrlLib import ModPythonRequest
    request = ModPythonRequest(req)
    install.run(request)
    request.flush()
    #return request.status
