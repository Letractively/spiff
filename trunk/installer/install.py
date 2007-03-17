#!/usr/bin/python
import sys, cgi, os.path
sys.path.append('../libs/')
from genshi.template       import TextTemplate
from genshi.template       import TemplateLoader
from Constructor           import *
from Constructor.Task      import *
from InstallGuard          import InstallGuard
from InstallIntegrator     import InstallIntegrator
from InstallExtension      import InstallExtension
from CreateDefaultSetup    import CreateDefaultSetup
from SetUserPassword       import SetUserPassword

print 'Content-Type: text/html'
print

db_config_file = os.path.join(os.path.dirname(__file__), '../data/spiff.cfg')

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
constructor.append(SaveDBConfig(db_config_file))
constructor.append(CheckDBSupportsConstraints())

# Other installation tasks.
tasks = [
    CreateDir('../data/repo'),
    CreateDir('../data/uploads'),
    InstallGuard(),
    InstallIntegrator()
]
constructor.append(CreateDefaultSetup('Creating default setup', tasks))
constructor.append(SetUserPassword('admin'))

# Install core extensions.
tasks = [
    InstallExtension('../plugins/Spiff'),
    InstallExtension('../plugins/Login'),
    InstallExtension('../plugins/AdminCenter'),
    InstallExtension('../plugins/UserManager'),
    InstallExtension('../plugins/ContentManager'),
    InstallExtension('../plugins/WikiPage')
]
constructor.append(CheckList('Installing core extensions', tasks))
constructor.append(InstallationCompleted())
result = constructor.install()
