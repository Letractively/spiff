#!/usr/bin/python
import sys, cgi
sys.path.append('../libs/')
from genshi.template       import TextTemplate
from genshi.template       import TemplateLoader
from Constructor           import *
from Constructor.Task      import *
from InstallGuard          import InstallGuard
from InstallIntegrator     import InstallIntegrator
from CreateDefaultSetup    import CreateDefaultSetup

print 'Content-Type: text/html'
print

# Set Spiff Constructor up.
loader      = TemplateLoader(['.'])
template    = loader.load('install.tmpl', None, TextTemplate)
environment = WebEnvironment(cgi.FieldStorage(), template)
constructor = Constructor(environment)
constructor.set_app_version('0.1')

# Installation requirement checks.
checks = [CheckPythonVersion((2, 3, 0, '', 0)),
          DirExists('../data/'),
          FileIsWritable('../data/')]
constructor.append(CheckList('Checking installation requirements', checks))

# Database setup.
constructor.append(CollectDBInfo(['mysql4']))
constructor.append(CheckDBConnection())
#FIXME: Check whether InnoDB is supported.
#sql = 'SHOW VARIABLES LIKE "have_innodb"'

# Other installation tasks.
tasks = [
    CreateDir('../data/repo'),
    CreateDir('../data/uploads'),
    InstallGuard(),
    InstallIntegrator()
]
constructor.append(CreateDefaultSetup('Creating default setup', tasks))
constructor.append(InstallationCompleted())
result = constructor.install()
