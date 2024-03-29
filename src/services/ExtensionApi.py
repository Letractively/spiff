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
        self.__spiff        = spiff
        self.__guard        = kwargs['guard']
        self.__cache        = kwargs.get('cache')
        self.__page_db      = kwargs['page_db']
        self.__request      = kwargs['request']
        self.__http_headers = []
        self.__output       = ''
        self.template_render_time = 0


    def login(self, username, password):
        """
        Attempts to login the user with the given name/password.
        """
        return self.__spiff.login(username, password)


    def logout(self):
        return self.__spiff.logout()


    def set_requested_page(self, page):
        return self.__spiff.set_requested_page(page)


    def get_requested_page(self):
        return self.__spiff.get_requested_page()


    def get_env(self, name):
        return self.__request.get_env(name)


    def get_data(self):
        return self.__request.get_data()


    def post_data(self):
        return self.__request.post_data()


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


    def get_requested_uri(self, **kwargs):
        return self.__spiff.get_requested_uri(**kwargs)


    def append_http_headers(self, *args, **kwargs):
        for key in kwargs:
            self.__http_headers.append((key, kwargs[key]))


    def get_current_user(self):
        return self.__spiff.get_current_user()


    def current_user_may(self, action_handle, page = None):
        return self.__spiff.current_user_may(action_handle, page)


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
        if not kwargs.has_key('error'):
            kwargs['error'] = None
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
