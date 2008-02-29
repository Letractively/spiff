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
sys.path.insert(0, 'libs/Guard/src/')
sys.path.insert(0, 'libs/Integrator/src/')
sys.path.insert(0, 'libs/Warehouse/src/')
sys.path.insert(0, 'libs/WikiMarkup/src/')
sys.path.insert(0, 'objects')
sys.path.insert(0, 'services')
sys.path.insert(0, 'functions')
import MySQLdb, Guard
from sqlalchemy      import *
from urlutil         import get_uri, get_request_uri
from gettext         import gettext
from string          import split
from Integrator      import PackageManager
from ConfigParser    import RawConfigParser
from ExtensionApi    import ExtensionApi
from genshi.template import TemplateLoader
from genshi.template import TextTemplate
from genshi.template import MarkupTemplate
from PageDB          import PageDB
from UserDB          import UserDB
from CacheDB         import CacheDB
from Session         import Session
from SpiffPackage    import SpiffPackage

__version__ = '0.0.1'
bench       = {'start': time.clock()}
cfg_file    = 'data/spiff.cfg'
package_dir = 'data/repo/'
cfg         = RawConfigParser()
cfg.read(cfg_file)

def get_admin_links(loader, user):
    tmpl = loader.load('admin_header.tmpl', None, MarkupTemplate)
    return tmpl.generate(web_dir       = '/web',
                         uri           = get_uri,
                         request_uri   = get_request_uri,
                         current_user  = user,
                         may_edit_page = True,
                         txt           = gettext).render('xhtml')


def get_headers(api, content_type = 'text/html; charset=utf-8'):
    # Print the HTTP header.
    headers = api.get_http_headers()
    output  = 'Content-Type: %s\n' % content_type
    for k, v in headers:
        output += '%s: %s\n' % (k, v)
    output += '\n'

    # Load and display the HTML header.
    session = api.get_session()
    loader  = TemplateLoader(['web'])
    tmpl    = loader.load('header.tmpl',  None, TextTemplate)
    output += tmpl.generate(web_dir      = '/web',
                            current_user = session.get_user(),
                            txt          = gettext).render('text')

    # If the user has special rights, show links to the admin pages.
    if session.may('edit'):
        output += get_admin_links(loader, session.get_user())

    # Display the top banner.
    tmpl    = loader.load('header2.tmpl', None, MarkupTemplate)
    output += tmpl.generate(web_dir      = '/web',
                            uri          = get_uri,
                            request_uri  = get_request_uri,
                            current_user = session.get_user(),
                            txt          = gettext).render('xhtml')
    return output


def get_footer():
    loader = TemplateLoader(['web'])
    tmpl   = loader.load('footer.tmpl', None, TextTemplate)
    return tmpl.generate(web_dir = '/web',
                         txt     = gettext).render('text')


def print_benchmark(api = None):
    tmpl_render_time = api and api.template_render_time or 0
    bench['total']   = time.clock() - bench['start']
    times = [['total',
              'Total rendering time is %ss.' % bench.get('total', 0),
              False],
             ['set_up',
              'Set-up time is %ss.' % bench.get('set_up', 0),
              False],
             ['page_find',
              'Time for looking up the page is %ss.' % bench.get('page_find', 0),
              False],
             ['cache_check',
              'Spent %ss checking the cache.' % bench.get('cache_check', 0),
              False],
             ['package_load',
              'Spent %ss loading packages.' % bench.get('package_load', 0),
              False],
             ['permission_check',
              'Time spent checking permissions is %ss.' % bench.get('permission_check', 0),
              False],
             ['render_header',
              'Render time spent on header is %ss.' % bench.get('render_header', 0),
              False],
             ['render_plugins',
              'Render time spent in plugins is %ss.' % bench.get('render_plugins', 0),
              False],
             ['render_footer',
              'Render time spent in footer is %ss.' % bench.get('render_footer', 0),
              False],
             ['cache_add',
              'Time spent adding to cache is %ss.' % bench.get('cache_add', 0),
              False],
             ['template',
              'Spent %ss rendering templates.' % tmpl_render_time,
              False]]
    for item in times:
        try:
            if cfg.getboolean('benchmark', 'show_%s_time' % item[0]):
                item[2] = True
        except:
            pass
    if True not in [s for n, t, s in times]:
        return
    print '<table width="100%">'
    for name, text, show in times:
        if not show:
            continue
        print '  <tr>'
        print '    <td class="benchmark" id="%s" align="center">' % name
        print '    %s' % text
        print '    </td>'
        print '  </tr>'
    print '</table>'


def run():
    ###
    # Start the magic.
    ###
    if not os.path.exists('data/spiff.cfg'):
        print 'Content-Type: text/html; charset=utf-8'
        print
        print 'Please configure Spiff before accessing this site.<br/>'
        print 'The INSTALL file shipped with the Spiff installation contains'
        print 'instructions on how this is done.'
        return

    if os.path.exists('install'):
        print 'Content-Type: text/html; charset=utf-8'
        print
        print 'Out of security reasons, please delete the install/ directory'
        print 'before accessing this page.'
        return

    # Read config.
    dbn = cfg.get('database', 'dbn')

    # Connect to MySQL and set up Spiff Guard.
    db    = create_engine(dbn)
    guard = Guard.DB(db)
    #print 'Content-Type: text/html; charset=utf-8'
    #print
    #db.echo = 1

    # Find the current page using the given cgi variables.
    page_db            = PageDB(guard)
    user_db            = UserDB(guard)
    get_data           = cgi.parse_qs(os.environ["QUERY_STRING"])
    post_data          = cgi.FieldStorage()
    page_handle        = get_data.get('page', ['default'])[0]
    start              = time.clock()
    page               = page_db.get(page_handle)
    bench['page_find'] = time.clock() - start

    # Set up the session and the HTML cache.
    session         = Session(guard, requested_page = page)
    cache           = CacheDB(guard, session)
    bench['set_up'] = time.clock() - bench['start'] - bench['page_find']

    # Can not open some pages by addressing them directly.
    if get_data.has_key('page') \
      and page_db.is_system_page_handle(get_data.get('page')[0]):
        print 'Content-Type: text/html; charset=utf-8'
        print
        print 'error 403 (Forbidden)<br/>'
        print 'Can not open %s by addressing it directly.' % repr(page_handle)
        return

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
        return
    bench['page_find'] += time.clock() - start

    # If the output of ALL extensions is cached (combined), there is no need
    # to redraw the page, including headers and footer.
    # Note that the cache only returns pages corresponding to the permissions
    # of the current user, so this is safe.
    session.set_requested_page(page)
    start = time.clock()
    if os.environ['REQUEST_METHOD'] == 'GET':
        output               = cache.get_page()
        bench['cache_check'] = time.clock() - start
        if output is not None:
            print output
            print_benchmark()
            return
    bench['cache_check'] = time.clock() - start

    # Set up the plugin manager (Integrator). Note that the constructor
    # of PackageManager also associates the api with a reference to the
    # PackageManager instance.
    api = ExtensionApi(guard     = guard,
                       page_db   = page_db,
                       cache     = cache,
                       session   = session,
                       get_data  = get_data,
                       post_data = post_data)
    pm = PackageManager(guard, api, package = SpiffPackage)
    pm.set_package_dir(package_dir)

    bench['set_up'] = time.clock() - bench['start'] - bench['page_find']
    start           = time.clock()

    # Ending up here the entire page was not cached.
    # Make sure that the caller has permission to retrieve this page.
    # If the caller currently has no permission, load the login
    # extension to give it the opportunity to perform the login.
    start = time.clock()
    if (page.get_attribute('private') and not session.may('view')) \
      or api.get_post_data('login') is not None \
      or api.get_post_data('logout') is not None:
        page = page_db.get('admin/login')
        session.set_requested_page(page)
    bench['permission_check'] = time.clock() - start

    # Render the layout. This invokes the plugins, which in turn may
    # request some HTTP headers to be sent. So we need to fetch the 
    # list of headers after that!
    start  = time.clock()
    output = page.get_output(api)
    bench['render_plugins'] = time.clock() - start

    # Now that all plugins are completed we may retrieve a list of headers.
    start   = time.clock()
    headers = get_headers(api)
    bench['render_header'] = time.clock() - start

    # Get the footer, excluding benchmark information.
    start  = time.clock()
    footer = get_footer()
    bench['render_footer'] = time.clock() - start

    # Cache the page (if it is cacheable).
    start  = time.clock()
    output = headers + output + footer
    if page.is_cacheable() and len(api.get_http_headers()) == 0:
        cache.add_page(output)
    bench['cache_add'] = time.clock() - start

    # Yippie.
    print output
    print_benchmark(api)
