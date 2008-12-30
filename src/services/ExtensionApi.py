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
import os.path, sys, cPickle, time
from stat            import ST_MTIME
from gettext         import gettext
from SpiffIntegrator import Api
from pywsgi          import Url
from objects         import User
from objects         import PageAction

class ExtensionApi(Api):
    def __init__(self, spiff, **kwargs):
        Api.__init__(self)
        self.spiff            = spiff
        self.__guard          = kwargs['guard']
        self.__cache          = kwargs.get('cache')
        self.__page_db        = kwargs['page_db']
        self.__request        = kwargs['request']
        self.__current_user   = None
        self.__http_headers   = []
        self.__output         = ''
        self.template_render_time = 0


    def __get_action(self):
        return self.__guard.get_action(handle = 'view',
                                       type   = PageAction)


    def _get_permission_hash(self, user):
        """
        This function returns a string that identifies all permissions
        of the current user on the current group.
        """
        page   = self.get_requested_page()
        string = page.get_attribute('private') and 'p' or 'np'
        if user is None:
            return string
        guard = self.__guard
        acls  = guard.get_permission_list_with_inheritance(actor    = user,
                                                           resource = page)
        for acl in acls:
            string += str(acl)
        return sha.new(string).hexdigest()


    def login(self, username, password):
        """
        Attempts to login the user with the given name/password.
        """
        #print "Login requested for user '%s'." % username
        if username is None or password is None:
            return None
        user = self.__guard.get_resource(handle = username,
                                         type   = User)
        if user is None:
            return None
        if user.is_inactive():
            return None
        if not user.has_password(password):
            return None
        #print "Logging in with sid %s..." % self.__sid
        user.set_attribute('sid',             self.__request.get_session().get_id())
        user.set_attribute('permission_hash', self._get_permission_hash(user))
        self.__guard.save_resource(user)
        self.__current_user = user
        return headers


    def logout(self):
        self.__current_user = None
        self.__sid          = None
        return {'Set-Cookie': 'sid=''; expires=Thu, 01-JAN-1970 00:00:00 GMT;'}


    def get_requested_page(self):
        return self.spiff.get_requested_page()


    def get_env(self, name):
        return self.__request.get_env(name)


    def __get_caller(self):
        frame = sys._getframe(2)
        try:
            caller = frame.f_locals['self']
        finally:
            del frame
        return caller


    def __get_package_from_key(self, key):
        assert key is not None
        return self._manager.get_package_from_id(key)


    def get_data_dir(self):
        return os.path.join(os.path.dirname(__file__), '..', 'data')


    def get_get_data(self, name = None, unpack = True):
        value = self.__request.get_get_data(name)
        if name is None:
            return value
        if value is None:
            return None
        if unpack:
            return value[0]
        return value


    def get_post_data(self, name = None, unpack = True):
        value = self.__request.get_post_data(name)
        if name is None:
            return value
        if value is None:
            return None
        if unpack:
            return value[0]
        return value


    def get_requested_uri(self, **kwargs):
        return self.__request.get_current_url(**kwargs).get_string()


    def append_http_headers(self, *args, **kwargs):
        for key in kwargs:
            self.__http_headers.append((key, kwargs[key]))


    def get_http_headers(self):
        #FIXME: Do we need to check the permission of the caller?
        return self.__http_headers


    def get_current_user(self):
        return self.spiff.get_current_user()


    def current_user_may(self, action_handle, page = None):
        if page is None:
            page = self.spiff.get_requested_page()

        # If the page is publicly available there's no need to ask the DB.
        private = page.get_attribute('private') or False
        if action_handle == 'view' and not private:
            return True

        # Get the currently logged in user.
        user = self.get_current_user()
        if user is None:
            return False

        # Ask the DB whether permission shall be granted.
        action = self.__guard.get_action(type   = PageAction,
                                         handle = action_handle)
        if self.__guard.has_permission(user, action, page):
            return True
        return False 


    def get_db(self):
        #FIXME: Check permission of the caller!
        return self.__guard.db


    def get_guard(self):
        #FIXME: Check permission of the caller!
        return self.__guard


    def get_page_db(self):
        return self.__page_db


    def get_cache(self):
        return self.__cache


    def flush_cache(self, key, **kwargs):
        package = self.__get_package_from_key(key)
        assert package is not None
        self.__cache.flush(package.get_handle(), **kwargs)


    def get_integrator(self):
        #FIXME: Check permission of the caller!
        assert self._manager # Api must be associated to the manager first.
        return self._manager


    def get_session(self):
        #FIXME: Check permission of the caller!
        return self.__session


    def get_package(self, descriptor):
        pass #FIXME


    def render(self, filename, *args, **kwargs):
        #FIXME: Do we need to check the permission of the caller?
        assert filename is not None
        # Find the object that made the API call.
        extension = self.__get_caller()
        assert extension

        # Point dirname to the path of the plugin that made the call.
        classname  = '%s' % extension.__module__
        subdirname = classname.split('.')[0]
        dirname    = os.path.join('data/repo/', subdirname)
        tmpl_path  = os.path.join(dirname, filename)
        cache_dir  = os.path.join(self.get_data_dir(), 'cache')
        cache_file = dirname.replace('/', '_') + filename
        cache_path = os.path.join(cache_dir, cache_file)
        tmpl       = None

        # Load and display the template.
        tmpl_mtime = os.stat(tmpl_path)[ST_MTIME]
        try:
            cache_mtime = os.stat(cache_path)[ST_MTIME]
        except:
            cache_mtime = 0
        start = time.clock()
        if cache_mtime < tmpl_mtime:
            from genshi.template import TemplateLoader
            from genshi.template import MarkupTemplate
            loader = TemplateLoader([dirname])
            tmpl   = loader.load(filename, None, MarkupTemplate)
            #fp     = open(cache_path, 'w')
            #cPickle.dump(tmpl, fp)
            #fp.close()
        else:
            fp   = open(cache_path, 'r')
            tmpl = cPickle.load(fp)
            fp.close()
        self.__output = tmpl.generate(plugin_dir  = dirname,
                                      web_dir     = '/web',
                                      uri         = Url(self.__request),
                                      puri        = self.get_requested_uri,
                                      request_uri = self.get_requested_uri,
                                      txt         = gettext,
                                      **kwargs).render('xhtml')
        self.template_render_time += time.clock() - start


    def get_output(self):
        #FIXME: Check the permission of the caller.
        return self.__output


    def clear_output(self):
        #FIXME: Check the permission of the caller.
        self.__output = ''


if __name__ == '__main__':
    import unittest

    class ExtensionApiTest(unittest.TestCase):
        def runTest(self):
            #FIXME: Implement test.
            pass
            
    testcase = ExtensionApiTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
