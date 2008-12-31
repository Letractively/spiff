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
import sys, cgi, os, os.path, config, sha
import MySQLdb, SpiffGuard, config
from SpiffIntegrator import PackageManager
from Benchmarker     import Benchmarker
from sqlalchemy      import *
from genshi.template import TemplateLoader
from genshi.template import TextTemplate
from genshi.template import MarkupTemplate
from gettext         import gettext
from string          import split
from ConfigParser    import RawConfigParser
from services        import ExtensionApi, PageDB, UserDB, CacheDB
from objects         import SpiffPackage, User, PageAction

class Spiff(object):
    def __init__(self, request):
        self.request        = request
        self.guard          = None
        self.current_user   = None
        self.requested_page = None
        self.bench          = Benchmarker()
        self.output         = ''
        #self.db.echo = 1


    def get_guard(self):
        if self.guard is None:
            db         = create_engine(config.cfg.get('database', 'dbn'))
            self.guard = SpiffGuard.DB(db)
        return self.guard


    def get_env(self, name): #FIXME: Probably shouldn't be here.
        return self.request.get_env(name)


    def set_requested_page(self, page):
        self.requested_page = page


    def get_requested_page(self):
        return self.requested_page


    def get_requested_uri(self, **kwargs):
        return self.request.get_current_url(**kwargs).get_string()


    def _get_permission_hash(self, user):
        """
        This function returns a string that identifies all permissions
        of the given user on the current group.
        FIXME: this sounds like a hack, and should not be here anyway.
        """
        page   = self.get_requested_page()
        string = page.get_attribute('private') and 'p' or 'np'
        if user is None:
            return string
        acls = self.guard.get_permission_list_with_inheritance(actor    = user,
                                                               resource = page)
        for acl in acls:
            string += str(acl)
        return sha.new(string).hexdigest()


    def login(self, username, password):
        """
        Attempts to login the user with the given name/password.
        """
        if username is None or password is None:
            return None
        user = self.guard.get_resource(handle = username, type = User)
        if user is None:
            return None
        if user.is_inactive():
            return None
        if not user.has_password(password):
            return None
        permission_key = self._get_permission_hash(user)
        self.request.get_session().data().set('user_id',        user.get_id())
        self.request.get_session().data().set('permission_key', permission_key)
        self.current_user = user
        return user


    def logout(self):
        self.request.get_session().destroy()
        self.current_user = None


    def get_current_user(self):
        if self.current_user is not None:
            return self.current_user
        session = self.request.get_session()
        if session is None:
            return None
        sid = session.get_id()
        assert sid is not None
        user_id = session.data().get('user_id')
        if user_id is None:
            return None
        user = self.guard.get_resource(id = user_id, type = User)
        if user is None:
            return None
        self.current_user = user
        return self.current_user


    def current_user_may(self, action_handle, page = None):
        if page is None:
            page = self.get_requested_page()

        # If the page is publicly available there's no need to ask the DB.
        private = page.get_attribute('private') or False
        if action_handle == 'view' and not private:
            return True

        # Get the currently logged in user.
        user = self.get_current_user()
        if user is None:
            return False

        # Ask the DB whether permission shall be granted.
        action = self.guard.get_action(type   = PageAction,
                                       handle = action_handle)
        if self.guard.has_permission(user, action, page):
            return True
        return False 


    def _render_text_template(self, filename, **kwargs):
        loader       = TemplateLoader(['web'])
        tmpl         = loader.load(filename, None, TextTemplate)
        self.output += tmpl.generate(web_dir      = '/web',
                                     current_user = self.get_current_user(),
                                     txt          = gettext,
                                     **kwargs).render('text')


    def _render_xhtml_template(self, filename, **kwargs):
        loader       = TemplateLoader(['web'])
        tmpl         = loader.load(filename, None, MarkupTemplate)
        self.output += tmpl.generate(web_dir      = '/web',
                                     uri          = self.get_requested_uri,
                                     request_uri  = self.get_requested_uri,
                                     current_user = self.get_current_user(),
                                     txt          = gettext,
                                     **kwargs).render('xhtml')


    def _render_headers(self):
        self._render_text_template('header.tmpl', styles = [])
        if self.current_user_may('edit'):
            self._render_xhtml_template('admin_header.tmpl', may_edit_page = True)
        self._render_xhtml_template('header2.tmpl')


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

        # Find the current page using the given cgi variables.
        page_db     = PageDB(self.get_guard())
        user_db     = UserDB(self.get_guard())
        page_handle = self.request.get_get_data('page', ['default'])[0]
        page        = page_db.get(page_handle)
        self.bench.snapshot('page_find', 'Looked up the page in %ss.')

        # Set up the HTML cache.
        self.request.start_session()
        cache = CacheDB(self, self.get_guard())
        self.bench.snapshot('set_up', 'Set-up time is %ss.')

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
        self.bench.snapshot('page_open', 'Opened the page in %ss.')

        # If the output of ALL extensions is cached (combined), there is no need
        # to redraw the page, including headers and footer.
        # Note that the cache only returns pages corresponding to the permissions
        # of the current user, so this is safe.
        self.requested_page = page
        if self.request.get_env('REQUEST_METHOD') == 'GET':
            output               = cache.get_page()
            self.bench.snapshot('cache_check', 'Spent %ss checking the cache.')
            if output is not None:
                self.request.write(output)
                self.request.write(get_benchmark())
                return
        self.bench.snapshot('cache_check', 'Spent %ss checking the cache.')

        # Set up the plugin manager (Integrator). Note that the constructor
        # of PackageManager also associates the api with a reference to the
        # PackageManager instance.
        api = ExtensionApi(self,
                           guard   = self.get_guard(),
                           page_db = page_db,
                           cache   = cache,
                           request = self.request)
        pm = PackageManager(self.get_guard(), api, package = SpiffPackage)
        pm.set_package_dir(config.package_dir)
        self.bench.snapshot('package_load', 'Package manager loaded in %ss.')

        # Ending up here the entire page was not cached.
        # Make sure that the caller has permission to retrieve this page.
        # If the caller currently has no permission, load the login
        # extension to give it the opportunity to perform the login.
        if (page.get_attribute('private') and not self.current_user_may('view')) \
          or self.request.has_post_data('login') \
          or self.request.has_post_data('logout'):
            page = page_db.get('admin/login')
            self.requested_page = page
        self.bench.snapshot('permission_check', 'Permission checked in %ss.')

        # Render the layout. This invokes the plugins, which in turn may
        # request some HTTP headers to be sent. So we need to fetch the 
        # list of headers after that!
        page_output = page.get_output(api)
        self.bench.snapshot('render_plugins', 'Plugins rendered in %ss.')

        # Now that all plugins are completed we may retrieve a list of headers.
        self._render_headers()
        self.bench.snapshot('render_header', 'Headers rendered in %ss.')

        self.output += page_output

        # Get the footer, excluding benchmark information.
        self._render_text_template('footer.tmpl')
        self.bench.snapshot('render_footer', 'Footer rendered in %ss.')

        # Cache the page (if it is cacheable).
        if page.is_cacheable() and len(self.request.get_headers()) == 0:
            cache.add_page(self.output)
        self.bench.snapshot('cache_add', 'Added to cache in %ss.')

        # Yippie.
        self.request.write(self.output)
        self.bench.snapshot_total('total', 'Total rendering time is %ss.')
        self.request.write(self.bench.get_html())
