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
import sys, cgi, os, os.path
from string import split
sys.path.append('libs')
import MySQLdb, Integrator
from sqlalchemy      import *
from functions       import *
from ConfigParser    import RawConfigParser
from ExtensionApi    import ExtensionApi
from Layout          import Layout
from genshi.template import TemplateLoader
from genshi.template import TextTemplate
from genshi.template import MarkupTemplate
import Guard


def show_admin_links(loader, user, integrator):
    # Check for admin permissisions
    edit_layout = extension_api.has_permission('edit_layout')
    if not edit_layout:
        return

    tmpl    = loader.load('admin_header.tmpl', None, MarkupTemplate)
    web_dir = get_mod_rewrite_prevented_uri('web')
    print tmpl.generate(web_dir      = web_dir,
                        uri          = get_uri,
                        request_uri  = get_request_uri,
                        current_user = user,
                        edit_layout  = edit_layout,
                        txt          = gettext).render('xhtml')


def send_headers(integrator,
                 user,
                 page,
                 headers      = [],
                 content_type = 'text/html; charset=utf-8'):
    # Print the HTTP header.
    print 'Content-Type: %s' % content_type
    for k, v in headers:
        print '%s: %s\n' % (k, v)
    print

    # Load and display the HTML header.
    loader  = TemplateLoader(['web'])
    tmpl    = loader.load('header.tmpl',  None, TextTemplate)
    web_dir = get_mod_rewrite_prevented_uri('web')
    print tmpl.generate(web_dir      = web_dir,
                        current_user = user,
                        txt          = gettext).render('text')

    # If the user has special rights, show links to the admin pages.
    if user is not None:
        show_admin_links(loader, user, integrator)

    # Display the top banner.
    tmpl = loader.load('header2.tmpl', None, MarkupTemplate)
    print tmpl.generate(web_dir      = web_dir,
                        uri          = get_uri,
                        request_uri  = get_request_uri,
                        current_user = user,
                        txt          = gettext).render('xhtml')


def send_footer():
    loader  = TemplateLoader(['web'])
    tmpl    = loader.load('footer.tmpl', None, TextTemplate)
    web_dir = get_mod_rewrite_prevented_uri('web')
    print tmpl.generate(web_dir = web_dir,
                        txt     = gettext).render('text')


def find_requested_page(get_data):
    if not get_data.has_key('page'):
        return 'homepage'
    return get_data['page'][0]


def get_login_page(guard_db):
    login = guard_db.get_resource_from_handle('admin/login', 'content')
    assert login is not None
    return login


def log_in(guard_db, integrator, page):
    """
    Returns a tuple of boolean: (did_login, page_open_sent)
    """
    user = extension_api.get_login().get_current_user()
    if user:
        # Bail out if the user is already logged in and has permission.
        view = guard_db.get_action_from_handle('view', 'content_permissions')
        assert view is not None
        if guard_db.has_permission(user, view, page):
            return (True, False)

    # Ending up here, the user is not logged in or has insufficient rights.
    # Load the login form extension.
    login = get_login_page(guard_db)
    descriptor = login.get_attribute('extension')
    assert descriptor is not None
    extension = integrator.load_extension_from_descriptor(descriptor)

    # The extension can fetch this signal and perform the login.
    extension_api.emit_sync('spiff:page_open')

    # The login form might have performed a successful login.
    user = extension_api.get_login().get_current_user()
    if user is None:
        return (False, True)

    # Check permissions again.
    view = guard_db.get_action_from_handle('view', 'content_permissions')
    assert view is not None
    if guard_db.has_permission(user, view, page):
        return (True, True)
    return (False, True)


###
# Start the magic.
###
#send_headers(None, None, None)

if not os.path.exists('data/spiff.cfg'):
    print 'Content-Type: text/html; charset=utf-8'
    print
    print 'Please configure Spiff before accessing this site.<br/>'
    print 'The INSTALL file shipped with the Spiff installation contains'
    print 'instructions on how this is done.'
    sys.exit()

if os.path.exists('install'):
    print 'Content-Type: text/html; charset=utf-8'
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
extension_api = ExtensionApi(requested_page = page,
                             guard_mod      = Guard,
                             guard_db       = guard_db,
                             get_data       = get_data,
                             post_data      = post_data)
integrator = Integrator.Manager(guard_db, extension_api)
integrator.set_extension_dir('data/repo')

# Can not open some pages by addressing them directly.
open_sys_page = False
if (page_handle == 'homepage'
    or page_handle == 'default'
    or page_handle.startswith('homepage/')
    or page_handle.startswith('default/')):
    open_sys_page = True
if open_sys_page and get_data.has_key('page'):
    print 'Content-Type: text/html; charset=utf-8'
    print
    print 'error 403 (Forbidden)'
    print 'Can not open the homepage by addressing it directly.'
    sys.exit()

# If the specific site was not found, cut the path until a page is found.
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

# If we still have not found a page, try our default page.
# If it has an extension that manages the entire tree instead of just a
# single page, use it.
if page is None:
    page = guard_db.get_resource_from_handle('default', 'content')
    assert page is not None
    extension_api.set_requested_page(page)
    descriptor = page.get_attribute('extension')
    extension  = integrator.load_extension_from_descriptor(descriptor)
    assert extension is not None
    try:
        is_recursive = extension.is_recursive
    except:
        is_recursive = False
    if not is_recursive:
        page = None

# If we still have no page, give 404.
if page is None:
    print 'Content-Type: text/html; charset=utf-8'
    print
    print 'error 404 (File not found)'
    sys.exit()

# Now that we may have redirected the user to another page, let the
# extension API know that.
extension_api.set_requested_page(page)

# Make sure that the caller has permission to retrieve this page.
page_open_sent = False
if page.get_attribute('private') or get_data.has_key('login'):
    (did_login, page_open_sent) = log_in(guard_db, integrator, page)
    if not did_login:
        page = get_login_page(guard_db)
        extension = None

if not page_open_sent:
    extension_api.emit_sync('spiff:page_open')

# If requested, load the layout editor.
if get_data.has_key('edit_layout'):
    page = guard_db.get_resource_from_handle('admin/layout', 'content')

# Send headers.
extension_api.emit_sync('spiff:header_before')
send_headers(integrator,
             extension_api.get_login().get_current_user(),
             page,
             extension_api.get_http_headers())
extension_api.emit_sync('spiff:header_after')

# Render the layout.
extension_api.emit_sync('spiff:render_before')
layout = Layout(integrator, extension_api, page)
layout.render()
extension_api.emit_sync('spiff:render_after')

# Send the footer.
extension_api.emit_sync('spiff:footer_before')
send_footer()
extension_api.emit_sync('spiff:footer_after')
extension_api.emit_sync('spiff:page_done')
