import sys, os, os.path
sys.path.insert(0, 'libs')
sys.path.insert(0, 'libs/Guard/src/')
sys.path.insert(0, 'libs/Integrator/src/')
sys.path.insert(0, 'services')
import MySQLdb, Guard, spiff, shutil
from sqlalchemy   import *
from Integrator   import PackageManager, \
                         version_is_greater, \
                         InvalidDescriptor
from ConfigParser import RawConfigParser
from ExtensionApi import ExtensionApi
from FooLib       import OptionParser
from PageDB       import PageDB
from Session      import Session
from traceback    import print_exc
from tempfile     import mkdtemp
from SpiffPackage import SpiffPackage


actions = ('check_dependencies',
           'create',
           'install',
           'list',
           'remove',
           'show',
           'test',
           'update')

def usage():
    print "Spiff %s" % spiff.__version__
    print "Copyright (C) 2007 by Samuel Abels <http://debain.org>."
    print "Syntax: python pkg.py [options] action package [package ...]"
    print "  action:  Any of the following:"
    print "             ", "\n              ".join(actions)
    print "  package: File or directory that contains the package. You may"
    print "           specify multiple files at the same time."
    print "  options: The following list of options are supported:"
    print "                  --version  Prints the version number."
    print "              -h, --help     Prints this help."

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
    assert action == 'list' or len(packages) > 0
except:
    usage()
    sys.exit(1)

# Check syntax.
if action not in actions:
    usage()
    print "Unknown action %s" % action
    sys.exit(1)

# Check whether the given package files exist.
if action not in ('create', 'remove', 'list'):
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
pm = PackageManager(guard, api, package = SpiffPackage)
pm.set_package_dir(spiff.package_dir)


def pkg_check_dependencies(pm, package):
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


def pkg_create(pm, directory):
    if os.path.exists(directory):
        print "%s: file already exists" % directory
        return False

    print "Creating an empty package in %s." % directory
    package = SpiffPackage(os.path.basename(directory))
    package.set_author('Unknown Author')
    package.set_author_email('unknown@unknown.com')
    package.set_version('0.0.1')
    package._add_listener('spiff:page_open')
    package._add_dependency('spiff', 'runtime')
    package._add_dependency('spiff', 'installtime')
    pm.create_package(directory, package)

    # Insert additional files.
    open(os.path.join(directory, 'index.phtml'), 'w').close()
    return True


def pkg_install(pm, package):
    if not pkg_check_dependencies(pm, package):
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
        return pkg_update(pm, package)
    print "Installing new package %s." % package.get_name()
    try:
        pm.install_package(package)
    except Exception, e:
        print "Installation failed:", e
        return False
    return True


def pkg_remove(pm, descriptor):
    try:
        package = pm.get_package_from_descriptor(descriptor)
    except InvalidDescriptor, e:
        print e
        return False
    if package is None:
        print "Package %s not found in database" % descriptor
        return False
    depends = pm.get_package_list(depends = package)
    if len(depends) > 0:
        depend = ['%s=%s' % (d.get_handle(), d.get_version()) for d in depends]
        descr  = '%s=%s' % (package.get_handle(), package.get_version())
        print "Can't remove %s, because the following packages use it:" % descr
        print '\n'.join(depend)
        return False
    handle  = package.get_handle()
    version = package.get_version()
    print "Removing package %s %s as requested." % (handle, version)
    pm.remove_package(package)
    return True


def pkg_show(pm, package):
    package.dump()
    return True


def pkg_list(pm, descriptor = None):
    packages = pm.get_package_list()
    for package in packages:
        try:
            if descriptor is None or package.matches(descriptor):
                print package
        except InvalidDescriptor, e:
            print e
            return False
    return True


def pkg_test(pm, package):
    print "Testing %s..." % package.get_name()
    # Set up.
    tmpdir = mkdtemp('')
    pm.set_package_dir(tmpdir)

    # Test.
    print "Installing in %s" % tmpdir
    try:
        pm.test_package(package)
    except:
        print 'Error: Test failed!'
        shutil.rmtree(tmpdir)
        raise

    # Done.
    print 'Test successfully completed!'
    shutil.rmtree(tmpdir)
    return True


def pkg_update(pm, package):
    if not pkg_check_dependencies(pm, package):
        return False
    installed = pm.get_package_from_descriptor(package.get_handle())
    if installed is None:
        descr = '%s=%s' % (installed.get_handle(), installed.get_version())
        print "Package %s not installed, so not updating." % descr
        return False
    print "Replacing package as requested."
    #FIXME
    print "!! Update functionality is not yet implemented..."
    return True

if action == 'list' and len(packages) == 0:
    pkg_list(pm)

for filename in packages:
    if action in ('create', 'remove', 'list'):
        result = locals()['pkg_' + action](pm, filename)
    else:
        package = pm.read_package(filename)
        result  = locals()['pkg_' + action](pm, package)
    if result is False:
        sys.exit(1)
