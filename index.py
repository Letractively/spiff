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
import sys, cgi, os, os.path, time
sys.path.insert(0, 'libs')
sys.path.insert(0, 'objects')
sys.path.insert(0, 'services')
sys.path.insert(0, 'functions')
import MySQLdb, Guard, Integrator
from sqlalchemy      import *
from urlutil         import get_uri, \
                            get_request_uri, \
                            get_mod_rewrite_prevented_uri
from gettext         import gettext
from string          import split
from ConfigParser    import RawConfigParser
from ExtensionApi    import ExtensionApi
from Layout          import Layout
from genshi.template import TemplateLoader
from genshi.template import TextTemplate
from genshi.template import MarkupTemplate
from User            import User
from Group           import Group
from Page            import Page
from UserAction      import UserAction
from PageAction      import PageAction
from PageDB          import PageDB
from Session         import Session

start_time = time.clock()

def show_admin_links(loader, user):
    tmpl    = loader.load('admin_header.tmpl', None, MarkupTemplate)
    web_dir = get_mod_rewrite_prevented_uri('web')
    print tmpl.generate(web_dir       = web_dir,
                        uri           = get_uri,
                        request_uri   = get_request_uri,
                        current_user  = user,
                        may_edit_page = True,
                        txt           = gettext).render('xhtml')


def send_headers(api, content_type = 'text/html; charset=utf-8'):
    # Print the HTTP header.
    headers = api.get_http_headers()
    print 'Content-Type: %s' % content_type
    for k, v in headers:
        print '%s: %s' % (k, v)
    print

    # Load and display the HTML header.
    session = api.get_session()
    loader  = TemplateLoader(['web'])
    tmpl    = loader.load('header.tmpl',  None, TextTemplate)
    web_dir = get_mod_rewrite_prevented_uri('web')
    print tmpl.generate(web_dir      = web_dir,
                        current_user = session.get_user(),
                        txt          = gettext).render('text')

    # If the user has special rights, show links to the admin pages.
    if session.may('edit'):
        show_admin_links(loader, session.get_user())

    # Display the top banner.
    tmpl = loader.load('header2.tmpl', None, MarkupTemplate)
    print tmpl.generate(web_dir      = web_dir,
                        uri          = get_uri,
                        request_uri  = get_request_uri,
                        current_user = session.get_user(),
                        txt          = gettext).render('xhtml')


def send_footer():
    loader      = TemplateLoader(['web'])
    tmpl        = loader.load('footer.tmpl', None, TextTemplate)
    web_dir     = get_mod_rewrite_prevented_uri('web')
    render_time = time.clock() - start_time
    print tmpl.generate(web_dir     = web_dir,
                        render_time = render_time,
                        txt         = gettext).render('text')


###
# Start the magic.
###
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
db      = create_engine(dbn)
guard   = Guard.DB(db)
page_db = PageDB(guard)
guard.register_type([User, Group, Page, UserAction, PageAction])

# Lookup the current page from the given cgi variables.
get_data    = cgi.parse_qs(os.environ["QUERY_STRING"])
post_data   = cgi.FieldStorage()
page_handle = get_data.get('page', ['homepage'])[0]
page        = page_db.get(page_handle)

# Set up the plugin manager (Integrator).
session = Session(guard, requested_page = page)
api     = ExtensionApi(guard     = guard,
                       page_db   = page_db,
                       session   = session,
                       get_data  = get_data,
                       post_data = post_data)
integrator = Integrator.Manager(guard, api)
integrator.set_package_dir('data/repo')

# Can not open some pages by addressing them directly.
if get_data.has_key('page') \
  and page_db.is_system_page_handle(get_data.get('page')[0]):
    print 'Content-Type: text/html; charset=utf-8'
    print
    print 'error 403 (Forbidden)<br/>'
    print 'Can not open %s by addressing it directly.' % repr(page_handle)
    sys.exit()

# If requested, load the content editor.
if get_data.has_key('new_page') or get_data.has_key('edit_page'):
    page = page_db.get('admin/page')

# If the specific site was not found, attempt to find a parent that
# handles content recursively.
elif page is None:
    page = page_db.get_responsible_page(page_handle)

# If we still have no page, give 404.
if page is None:
    print 'Content-Type: text/html; charset=utf-8'
    print
    print 'error 404 (File not found)'
    sys.exit()

# Make sure that the caller has permission to retrieve this page.
# If the caller currently has no permission, load the login
# extension to give it the opportunity to perform the login.
if page.get_attribute('private') and not session.may('view'):
    login      = page_db.get('admin/login')
    descriptor = login.get_attribute('extension')
    integrator.load_package_from_descriptor(descriptor)

# Now that we may have redirected the user to another page, let the
# extension API know that.
session.set_requested_page(page)

# The login extension may catch the following signal and perform the login.
api.emit_sync('spiff:page_open')

# At this point the login was performed. Check the permission.
if (page.get_attribute('private') and not session.may('view')) \
  or get_data.has_key('login'):
    page = page_db.get('admin/login')
    session.set_requested_page(page)

# Send headers.
api.emit_sync('spiff:header_before')
send_headers(api)
api.emit_sync('spiff:header_after')

# Render the layout.
api.emit_sync('spiff:render_before')
layout = Layout(api)
layout.render()
api.emit_sync('spiff:render_after')

# Send the footer.
api.emit_sync('spiff:footer_before')

send_footer()
api.emit_sync('spiff:footer_after')
api.emit_sync('spiff:page_done')
