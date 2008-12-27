#!/usr/bin/python
try:
    import spiff
    if __name__ == '__main__':
        from UrlLib import CgiRequest
        request = CgiRequest()
        spiff.run(request)
        request.flush()
except Exception, e:
    print 'Content-Type: text/html; charset=utf-8'
    print
    raise

def index(req):
    from mod_python import apache
    Request = apache.import_module('./UrlLib/Request.py')
    request = Request.ModPythonRequest(req)
    spiff.run(request)
    request.flush()
    #return request.status
