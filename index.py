#!/usr/bin/python
import sys, cgi, os, os.path
from string import split
sys.path.append('libs')
import MySQLdb, Integrator
from sqlalchemy   import *
from ConfigParser import RawConfigParser
from ExtensionApi import ExtensionApi
import Guard

#print 'Content-Type: text/html'
#print

def find_requested_page(get_data):
    if not get_data.has_key('page'):
        return 'homepage'
    return get_data['page'][0]


def log_in(guard_db, integrator, page):
    """
    Returns a tuple of boolean: (did_login, page_open_event_sent)
    """
    user = integrator.extension_api.get_login().get_current_user()
    if user:
        # Bail out if the user is already logged in and has permission.
        view = guard_db.get_action_from_handle('view', 'content_permissions')
        assert view is not None
        if guard_db.has_permission(user, view, page):
            return (True, False)

    # Ending up here, the user is not logged in or has insufficient rights.
    # Build a login form.
    login = guard_db.get_resource_from_handle('admin/login', 'content')
    assert login is not None
    descriptor = login.get_attribute('extension')
    assert descriptor is not None
    extension = integrator.load_extension_from_descriptor(descriptor)
    assert extension is not None

    # Diplay the form.
    integrator.extension_api.emit_sync('spiff:page_open')
    extension.on_render_request()

    # The login form might have performed a successful login.
    user = integrator.extension_api.get_login().get_current_user()
    if user is None:
        return (False, True)

    # Check permissions again.
    view = guard_db.get_action_from_handle('view', 'content_permissions')
    assert view is not None
    if guard_db.has_permission(user, view, page):
        return (True, True)
    return (False, True)


if not os.path.exists('data/spiff.cfg'):
    print 'Content-Type: text/html'
    print
    print 'Please configure Spiff before accessing this site.<br/>'
    print 'The INSTALL file shipped with the Spiff installation contains'
    print 'instructions on how this can be done.'
    sys.exit()

if os.path.exists('install'):
    print 'Content-Type: text/html'
    print
    print 'Out of security reasons, please delete the install/ directory before'
    print 'accessing this page.'
    sys.exit()

# Read config.
cfg = RawConfigParser()
cfg.read('data/spiff.cfg')
dbn = cfg.get('database', 'dbn')

# Connect to MySQL and set up Spiff Guard.
db       = create_engine(dbn)
guard_db = Guard.DB(db)

# Lookup the current page from the given cgi variables.
get_data    = cgi.parse_qs(os.environ["QUERY_STRING"])
post_data   = cgi.FieldStorage()
page_handle = find_requested_page(get_data)
page        = guard_db.get_resource_from_handle(page_handle, 'content')
extension   = None

# Set up the plugin manager (Integrator).
integrator = Integrator.Manager(guard_db,
                                ExtensionApi,
                                requested_page = page,
                                acldb          = guard_db,
                                guard_mod      = Guard,
                                get_data       = get_data,
                                post_data      = post_data)
integrator.set_extension_dir('data/repo')

# If the specific site was not found, cut the path until an page is found.
# Then look if the matching page has an extension that manages the entire
# tree instead of just a single page.
if page is None:
    # Retrieve the parent with the longest handle.
    while page_handle != '':
        stack       = split(page_handle, '/')
        page_handle = '/'.join(stack[:-1])
        page = guard_db.get_resource_from_handle(page_handle, 'content')
        if page is not None:
            break

    # Check whether it manages the subtree.
    if page is not None:
        descriptor = page.get_attribute('extension')
        extension  = integrator.load_extension_from_descriptor(descriptor)
        assert extension is not None
        try:
            is_recursive = extension.is_recursive
        except:
            is_recursive = False
        if not is_recursive:
            page = None

if page is None:
    print 'Content-Type: text/html'
    print
    print 'error 404'
    sys.exit()
integrator.extension_api.set_requested_page(page)

# Make sure that the caller has permission to retrieve this page.
page_open_event_sent = False
if page.get_attribute('private'):
    (did_log_in, page_open_event_sent) = log_in(guard_db, integrator, page)
    if not did_log_in:
        sys.exit()

# Load the appended plugins, if not done already.
if extension is None:
    descriptor = page.get_attribute('extension')
    extension  = integrator.load_extension_from_descriptor(descriptor)

if extension is None:
    print 'Content-Type: text/html'
    print
    print 'Page "%s" refers to unknown extension "%s"' % (page, descriptor)
    sys.exit()

if not page_open_event_sent:
    integrator.extension_api.emit_sync('spiff:page_open')
extension.on_render_request()
integrator.extension_api.emit_sync('spiff:extensions_done')
integrator.extension_api.emit_sync('spiff:page_done')
