#!/usr/bin/python
import sys
sys.path.append('../..')
from Constructor      import *
from Constructor.Task import *
import cgi

print 'Content-Type: text/html'
print

name        = 'Test Application'
version     = '0.1.2'
environment = WebEnvironment(cgi.FieldStorage())
constructor = Constructor(environment)
constructor.set_app_name(name)
constructor.set_app_version(version)
assert constructor.get_app_name()    == name
assert constructor.get_app_version() == version

# Test running some tasks.
constructor.append(LicenseAgreement('SERVE ME!'))
constructor.append(CollectDBInfo(['mysql4']))
constructor.append(InstallationCompleted())
result = constructor.install()
