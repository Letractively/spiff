#!/usr/bin/python
import os, os.path
os.chdir(os.path.dirname(__file__))
import config  # Configures sys.path.

# This handler runs the Spiff installer.
def handler(request):
    import install
    spiff.run(request)

# Hook for most adapters.
if __name__ == '__main__':
    from pywsgi import RequestHandler
    request_handler = RequestHandler(handler)

# Special cased hook for mod_python.
def index(req):
    from pywsgi import ModPythonRequest
    request = ModPythonRequest(req)
    request.handle(handler)
