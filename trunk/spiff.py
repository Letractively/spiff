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
import MySQLdb, SpiffGuard, config
from SpiffIntegrator import PackageManager
from sqlalchemy      import *
from genshi.template import TemplateLoader
from genshi.template import TextTemplate
from genshi.template import MarkupTemplate
from gettext         import gettext
from string          import split
from ConfigParser    import RawConfigParser
from mod_python      import apache

ExtensionApi    = apache.import_module('services/ExtensionApi').ExtensionApi
PageDB          = apache.import_module('services/PageDB').PageDB
UserDB          = apache.import_module('services/UserDB').UserDB
CacheDB         = apache.import_module('services/CacheDB').CacheDB
Session         = apache.import_module('services/Session').Session
SpiffPackage    = apache.import_module('objects/SpiffPackage').SpiffPackage

bench = {'start': time.clock()}

def get_benchmark(api = None):
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
            if config.cfg.getboolean('benchmark', 'show_%s_time' % item[0]):
                item[2] = True
        except:
            pass
    if True not in [s for n, t, s in times]:
        return ''
    result = '<table width="100%">'
    for name, text, show in times:
        if not show:
            continue
        result += '  <tr>'
        result += '    <td class="benchmark" id="%s" align="center">' % name
        result += '    %s' % text
        result += '    </td>'
        result += '  </tr>'
    result += '</table>'
    return result

class Runner(object):
    def __init__(self, request):
        self.request = request


    def _get_admin_links(self, api):
        api.render('admin_header.tmpl',
                   current_user  = user,
                   may_edit_page = True)
        return api.get_output()


    def _get_headers(self, api, content_type = 'text/html; charset=utf-8'):
        return '' #FIXME
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


    def _get_footer(self, api):
        return '' #FIXME
        loader = TemplateLoader(['web'])
        tmpl   = loader.load('footer.tmpl', None, TextTemplate)
        return tmpl.generate(web_dir = '/web',
                             txt     = gettext).render('text')


    def _check_configured(self):
        if os.path.exists(config.cfg_file):
            return True
        self.request.write('Configuration file (%s) not found.' % config.cfg_file)
        self.request.write(' Please configure Spiff before accessing this')
        self.request.write(' site.<br/>')
        self.request.write('The INSTALL file shipped with the Spiff')
        self.request.write(' installation contains instructions on how this')
        self.request.write(' is done.')
        return False


    def _check_installer_deleted(self):
        if config.cfg.has_option('debug', 'ignore_installer_directory'):
            return True
        if not os.path.exists(config.installer_dir):
            return True
        self.request.write('Out of security reasons, please delete the')
        self.request.write(' installer directory (%s).' % config.installer_dir)
        return False


    def run(self):
        if not self._check_configured():
            return
        if not self._check_installer_deleted():
            return

        # Connect to MySQL and set up Spiff Guard.
        dbn   = config.cfg.get('database', 'dbn')
        db    = create_engine(dbn)
        guard = SpiffGuard.DB(db)
        #db.echo = 1

        # Find the current page using the given cgi variables.
        page_db            = PageDB(guard)
        user_db            = UserDB(guard)
        post_data          = cgi.FieldStorage()
        page_handle        = self.request.get_get_data('page', ['default'])[0]
        start              = time.clock()
        page               = page_db.get(page_handle)
        bench['page_find'] = time.clock() - start

        # Set up the session and the HTML cache.
        session         = Session(guard,
                                  request        = self.request,
                                  requested_page = page)
        cache           = CacheDB(guard, session)
        bench['set_up'] = time.clock() - bench['start'] - bench['page_find']

        # Can not open some pages by addressing them directly.
        if self.request.has_get_data('page') \
          and page_db.is_system_page_handle(self.request.get_get_data('page')[0]):
            self.request.set_status(403)
            self.request.write('%s is a system page.' % repr(page_handle))
            return

        # If requested, load the content editor.
        if self.request.has_get_data('new_page') \
          or self.request.has_get_data('edit_page'):
            page = page_db.get('admin/page')

        # If the specific site was not found, attempt to find a parent that
        # handles content recursively.
        elif page is None:
            page = page_db.get_responsible_page(page_handle)

        # If we still have no page, give 404.
        if page is None:
            self.request.set_status(404)
            self.request.write('Default page not found.')
            return
        bench['page_find'] += time.clock() - start

        # If the output of ALL extensions is cached (combined), there is no need
        # to redraw the page, including headers and footer.
        # Note that the cache only returns pages corresponding to the permissions
        # of the current user, so this is safe.
        session.set_requested_page(page)
        start = time.clock()
        if self.request.get_env('REQUEST_METHOD') == 'GET':
            output               = cache.get_page()
            bench['cache_check'] = time.clock() - start
            if output is not None:
                self.request.write(output)
                self.request.write(get_benchmark())
                return
        bench['cache_check'] = time.clock() - start

        # Set up the plugin manager (Integrator). Note that the constructor
        # of PackageManager also associates the api with a reference to the
        # PackageManager instance.
        api = ExtensionApi(guard     = guard,
                           page_db   = page_db,
                           cache     = cache,
                           session   = session,
                           request   = self.request)
        pm = PackageManager(guard, api, package = SpiffPackage)
        pm.set_package_dir(config.package_dir)

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
        headers = self._get_headers(api)
        bench['render_header'] = time.clock() - start

        # Get the footer, excluding benchmark information.
        start  = time.clock()
        footer = self._get_footer(api)
        bench['render_footer'] = time.clock() - start

        # Cache the page (if it is cacheable).
        start  = time.clock()
        output = headers + output + footer
        if page.is_cacheable() and len(api.get_http_headers()) == 0:
            cache.add_page(output)
        bench['cache_add'] = time.clock() - start

        # Yippie.
        self.request.write(output)
        self.request.write(get_benchmark(api))

def run(request):
    sys.stderr = sys.stdout
    runner = Runner(request)
    return runner.run()
