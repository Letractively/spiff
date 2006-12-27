#!/usr/bin/python
import sys
sys.path.append('../..')
from Constructor      import *
from Constructor.Task import *
import cgi

print 'Content-Type: text/html'
print

# Set Spiff Constructor up.
environment = WebEnvironment(cgi.FieldStorage())
constructor = Constructor(environment)
constructor.set_app_name('Test Application')
constructor.set_app_version('0.1.2')

# Test some installation tasks.
pyver =  CheckPythonVersion((2, 3, 0, '', 0))
constructor.append(CheckList('Checking Requirements', [pyver]))
constructor.append(LicenseAgreement('SERVE ME!'))
constructor.append(CollectDBInfo(['mysql4']))
constructor.append(CheckDBConnection())
constructor.append(InstallationCompleted())
result = constructor.install()
