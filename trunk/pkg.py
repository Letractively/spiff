import sys, os, os.path
sys.path.insert(0, 'libs')
sys.path.insert(0, 'services')
import MySQLdb, Guard, spiff
from sqlalchemy   import *
from Integrator   import PackageManager, version_is_greater
from ConfigParser import RawConfigParser
from ExtensionApi import ExtensionApi
from FooLib       import OptionParser
from PageDB       import PageDB
from Session      import Session

actions = ('check_dependencies',
           'create',
           'install',
           'remove',
           'show',
           'test',
           'update')

def usage():
    print "Spiff %s" % spiff.__version__
    print "Copyright (C) 2007 by Samuel Abels <http://debain.org>."
    print "Syntax: python pkg.py [options] action package [package ...]"
    print "  action:   Any of the following:"
    print "              ", "              \n".join(actions)
    print "  package:  File or directory that contains the package."
    print "            You may specify multiple files at the same time."
    print "  options:  The following list of options are supported:"
    print "        --version  Prints the version number."
    print "    -h, --help     Prints this help."

# Define default options.
default_options = [
  ('version',           None, False),
  ('help',              'h',  False)
]

# Parse options.
try:
    options, args = OptionParser.parse_options(sys.argv, default_options)
except:
    usage()
    sys.exit(1)

# Show the help, if requested.
if options['help']:
    usage()
    sys.exit()

# Show the version number, if requested.
if options['version']:
    print "Spiff %s" % __version__
    sys.exit()

# Get package names.
try:
    action   = args.pop(0)
    packages = args
    assert len(packages) > 0
except:
    usage()
    sys.exit(1)

# Check syntax.
if action not in actions:
    usage()
    print "Unknown action %s" % action
    sys.exit(1)

# Check whether the given package files exist.
if action != 'create':
    for package in packages:
        if not os.path.exists(package):
            print "No such file: %s" % package
            sys.exit(1)

# Read config.
if not os.path.exists(spiff.cfg_file):
    print "Please configure Spiff before using this tool."
    sys.exit(1)
cfg = RawConfigParser()
cfg.read(spiff.cfg_file)
dbn = cfg.get('database', 'dbn')

# Connect to MySQL and set up Spiff Guard.
db    = create_engine(dbn)
guard = Guard.DB(db)

# Set up an environment for the package manager.
page_db = PageDB(guard)
page    = page_db.get('default')
session = Session(guard, requested_page = page)
api     = ExtensionApi(guard     = guard,
                       page_db   = page_db,
                       session   = session,
                       get_data  = object,
                       post_data = object)

# Init the package manager.
pm = PackageManager(guard, api)
pm.set_package_dir(spiff.package_dir)


def check_dependencies(pm, filename, package):
    print "Checking dependencies of %s..." % package.get_name(),
    error = False
    for dependency in package.get_dependency_list():
        if pm.get_package_from_descriptor(dependency) is None:
            print "\nUnmet dependency:", dependency
            error = True
    if error:
        return False
    print "done."
    return True


def create(pm, filename, package):
    print "Creating an empty package in %s." % filename
    pm.create_package(filename)
    open(os.path.join(filename, 'index.phtml'), 'w').close()
    return True


def install(pm, filename, package):
    if not check_dependencies(pm, filename, package):
        return False
    installed = pm.get_package_from_descriptor(package.get_handle())
    if installed is not None:
        old_version = installed.get_version()
        new_version = package.get_version()
        print "Package is already installed!"
        print "Installed: %s, new: %s." % (old_version, new_version)
        if version_is_greater(installed.get_version(), package.get_version()):
            print "Installed version is newer, downgrade aborted."
            return False
        return update(pm, filename, package)
    print "Installing new package %s." % package.get_name()
    try:
        installed = pm.install_package(filename)
    except Exception, e:
        print "Installation failed:", e
        return False
    return True


def remove(pm, filename, package):
    package = pm.get_package_from_descriptor(filename)
    if package is None:
        print "Package %s not found in database" % filename
        return False
    depends = pm.get_package_rdepends(package)
    if len(depends) > 0:
        print "Can't remove package, because the following packages use it:"
        print '\n'.join(depends)
        return False
    handle  = package.get_handle()
    version = package.get_version()
    print "Removing package %s %s as requested." % (handle, version)
    db.remove_package(package)
    return True


def show(pm, filename, package):
    print package
    return True


def test(pm, filename, package):
    #FIXME
    print "!! Test functionality is not yet implemented..."
    return True


def update(pm, filename, package):
    print "Replacing package as requested."
    #FIXME
    print "!! Update functionality is not yet implemented..."
    return True


for filename in packages:
    if action == 'create':
        package = None
    else:
        package = pm.read_package(filename)
    if not locals()[action](pm, filename, package):
        sys.exit(1)
    sys.exit()
