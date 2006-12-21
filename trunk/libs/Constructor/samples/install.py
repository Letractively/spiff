#!/usr/bin/python
import sys
sys.path.append('../..')
from Constructor import *
#import Constructor
import cgi

print 'Content-Type: text/html'
print

name        = 'Test Application'
version     = '0.1.2'
renderer    = WebRenderer()
#constructor = Constructor(renderer)
constructor = Constructor(renderer, cgi.FieldStorage())
constructor.set_app_name(name)
constructor.set_app_version(version)
assert constructor.get_app_name()    == name
assert constructor.get_app_version() == version

# Test running some tasks.
la_task = LicenseAgreementTask('SERVE ME!')
constructor.append(la_task)
assert constructor.install() == Task.interact
