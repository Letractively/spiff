#!/usr/bin/python
import sys, cgi
sys.path.append('../libs/')
from genshi.template       import TextTemplate
from genshi.template       import TemplateLoader
from Constructor           import *
from Constructor.Task      import *
from InstallGuard          import InstallGuard
from InstallIntegrator     import InstallIntegrator
from CreateActionSection   import CreateActionSection
from CreateAction          import CreateAction
from CreateResourceSection import CreateResourceSection
from CreateResourceGroup   import CreateResourceGroup
from CreateResource        import CreateResource

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

# Other installation tasks.
tasks = [
    CreateDir('../data/repo'),
    CreateDir('../data/uploads'),
    InstallGuard(),
    InstallIntegrator(),

    # User permissions.
    CreateActionSection('User Permissions', 'user_permissions'),
    CreateAction('Administer User', 'administer', 'user_permissions'),
    CreateAction('View User',       'view',       'user_permissions'),
    CreateAction('Create User',     'create',     'user_permissions'),
    CreateAction('Edit User',       'edit',       'user_permissions'),
    CreateAction('Delete User',     'delete',     'user_permissions'),

    # Content permissions.
    CreateActionSection('Content Permissions', 'content_permissions'),
    CreateAction('View Content',   'view',   'content_permissions'),
    CreateAction('Create Content', 'create', 'content_permissions'),
    CreateAction('Edit Content',   'edit',   'content_permissions'),
    CreateAction('Delete Content', 'delete', 'content_permissions'),

    # Users.
    CreateResourceSection('Users', 'users'),
    CreateResourceGroup('Everybody', 'everybody', 'users'),
    CreateResourceGroup('Administrators', 'administrators', 'users', 'everybody'),
    CreateResource('Administrator', 'root', 'users', 'administrators'),
    CreateResourceGroup('Users', 'users', 'users', 'everybody'),
    CreateResource('Anonymous George', 'anonymous', 'users', 'users')
]
constructor.append(CheckList('Creating default setup', tasks))
constructor.append(InstallationCompleted())
result = constructor.install()
