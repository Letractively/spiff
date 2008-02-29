import sys, os, os.path
sys.path.insert(0, 'libs')
sys.path.insert(0, 'libs/Guard/src/')
sys.path.insert(0, 'libs/Integrator/src/')
sys.path.insert(0, 'services')
import MySQLdb, Guard, spiff, shutil
from sqlalchemy   import *
from Integrator   import PackageManager, \
                         Package, \
                         version_is_greater, \
                         InvalidDescriptor
from ConfigParser import RawConfigParser
from ExtensionApi import ExtensionApi
from FooLib       import OptionParser
from PageDB       import PageDB
from Session      import Session
from traceback    import print_exc
from tempfile     import mkdtemp


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
pm = PackageManager(guard, api)
pm.set_package_dir(spiff.package_dir)


def check_dependencies(pm, package):
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


def create(pm, directory):
    if os.path.exists(directory):
        print "%s: file already exists" % directory
        return False

    print "Creating an empty package in %s." % directory
    package = Package(os.path.basename(directory))
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


def install(pm, package):
    if not check_dependencies(pm, package):
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
        return update(pm, package)
    print "Installing new package %s." % package.get_name()
    try:
        pm.install_package(package)
    except Exception, e:
        print "Installation failed:", e
        return False
    return True


def remove(pm, descriptor):
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


def show(pm, package):
    package.dump()
    return True


def list(pm, descriptor = None):
    packages = pm.get_package_list()
    for package in packages:
        try:
            if descriptor is None or package.matches(descriptor):
                print package
        except InvalidDescriptor, e:
            print e
            return False
    return True


def test(pm, package):
    print "Testing %s..." % package.get_name()
    tmpdir = mkdtemp('')
    pm.set_package_dir(tmpdir)
    print "Installing in %s" % tmpdir
    try:
        install(pm, package)
    except:
        print 'Error: Installation failed.'
        shutil.rmtree(tmpdir)
        raise

    # Ending up here, the package was properly installed in the target
    # directory. Load it.
    try:
        instance = package.load()
    except Exception, e:
        print 'Error: Unable to load package (%s).' % package.get_name()
        shutil.rmtree(tmpdir)
        if package.get_id() is not None:
            pm.remove_package(package)
        print_exc()
        return False

    # Check whether the package has an install() method.
    install_func = None
    try:
        install_func = getattr(instance, 'install')
    except:
        pass
    if install_func is not None:
        print "Package has an install() method."

    # Call the install method.
    try:
        pass
        # some day we may be smart enough to call install_func() here.
    except Exception, e:
        print 'Error in install_func() of %s.' % package.get_name()
        shutil.rmtree(install_dir)
        pm.remove_package_from_id(id)
        print_exc()
        return False

    return True


def update(pm, package):
    if not check_dependencies(pm, package):
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
    list(pm)

for filename in packages:
    if action in ('create', 'remove', 'list'):
        result = locals()[action](pm, filename)
    else:
        package = pm.read_package(filename)
        result  = locals()[action](pm, package)
    if result is False:
        sys.exit(1)
