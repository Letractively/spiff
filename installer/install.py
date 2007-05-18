#!/usr/bin/python
# Copyright (C) 2006 Samuel Abels, http://debain.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import sys, cgi, os.path
sys.path.append('../libs/')
from genshi.template       import TextTemplate
from genshi.template       import TemplateLoader
from Constructor           import *
from Constructor.Task      import *
from InstallGuard          import InstallGuard
from InstallIntegrator     import InstallIntegrator
from InstallWarehouse      import InstallWarehouse
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
    CreateDir('../data/warehouse'),
    InstallGuard(),
    InstallIntegrator(),
    InstallWarehouse()
]
constructor.append(CreateDefaultSetup('Creating default setup', tasks))
constructor.append(SetUserPassword('admin'))

# Install core extensions.
tasks = [
    InstallExtension('../plugins/Spiff'),
    InstallExtension('../plugins/Login'),
    InstallExtension('../plugins/AdminCenter'),
    InstallExtension('../plugins/UserManager'),
    InstallExtension('../plugins/PageEditor'),
    InstallExtension('../plugins/ExtensionManager'),
    InstallExtension('../plugins/WikiPage'),
    InstallExtension('../plugins/Apilogue'),
    InstallExtension('../plugins/Wishlist')
]
constructor.append(CheckList('Installing core extensions', tasks))
constructor.append(InstallationCompleted())
result = constructor.install()
