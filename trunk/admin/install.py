#!/usr/bin/python
import sys
sys.path.append('../libs/')
from genshi.template   import TextTemplate
from genshi.template   import TemplateLoader
from Constructor       import *
from Constructor.Task  import *
from InstallGuard      import InstallGuard
from InstallIntegrator import InstallIntegrator
import cgi

print 'Content-Type: text/html'
print

# Set Spiff Constructor up.
loader      = TemplateLoader(['.'])
template    = loader.load('install.tmpl', None, TextTemplate)
environment = WebEnvironment(cgi.FieldStorage(), template)
constructor = Constructor(environment)
constructor.set_app_name('Test Application')
constructor.set_app_version('0.1.2')

# Test some installation tasks.
constructor.append(CheckPythonVersion((2, 3, 0, '', 0)))
constructor.append(LicenseAgreement('SERVE ME!'))
constructor.append(CollectDBInfo(['mysql4']))
constructor.append(CheckDBConnection())
#FIXME: Check whether InnoDB is supported.
constructor.append(DirExists('../data/'))
constructor.append(FileIsWritable('../data/'))
constructor.append(CreateDir('../data/repo'))
constructor.append(CreateDir('../data/uploads'))
constructor.append(InstallGuard())
constructor.append(InstallIntegrator())
constructor.append(InstallationCompleted())
result = constructor.install()
