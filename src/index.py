#!/usr/bin/python
import os, os.path
os.chdir(os.path.dirname(__file__))
import config  # Configures sys.path.

# This handler runs Spiff.
def handler(request):
    from Spiff import Spiff
    Spiff(request).run()

# Hook for most adapters.
if __name__ == '__main__':
    from pywsgi import RequestHandler
    request_handler = RequestHandler(handler, session_dir = config.session_dir)

# Special cased hook for mod_python.
def index(req):
    from pywsgi import ModPythonRequest
    request = ModPythonRequest(req, session_dir = config.session_dir)
    request.handle(handler)
