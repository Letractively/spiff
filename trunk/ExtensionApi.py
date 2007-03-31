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
import os.path, sys
from functions       import *
from Integrator      import Api
from Cookie          import SimpleCookie
from Login           import Login
from genshi.template import TemplateLoader
from genshi.template import MarkupTemplate


class ExtensionApi(Api):
    def __init__(self, *args, **kwargs):
        assert kwargs.has_key('requested_page')
        assert kwargs.has_key('guard_mod')
        assert kwargs.has_key('guard_db')
        assert kwargs.has_key('get_data')
        assert kwargs.has_key('post_data')
        Api.__init__(self)
        self.__login          = Login(kwargs['guard_db'])
        self.__requested_page = kwargs['requested_page']
        self.__guard_mod      = kwargs['guard_mod']
        self.__guard_db       = kwargs['guard_db']
        self.__get_data       = kwargs['get_data']
        self.__post_data      = kwargs['post_data']
        self.__headers_sent   = False
        self.__http_headers   = []


    def _on_api_activate(self):
        self.add_listener(self.__on_headers_sent, "spiff:header_after")


    def __get_caller(self):
        frame = sys._getframe(2)
        try:
            caller = frame.f_locals['self']
        finally:
            del frame
        return caller


    def __on_headers_sent(self, args):
        self.__headers_sent = True


    def get_get_data(self, name, unpack = True):
        #FIXME: Do we need to check the permission of the caller?
        if not self.__get_data.has_key(name):
            return None
        if unpack:
            return self.__get_data[name][0]
        return self.__get_data[name]


    def get_post_data(self, name, unpack = True):
        #FIXME: Do we need to check the permission of the caller?
        if not self.__post_data.has_key(name):
            return None
        field = self.__post_data[name]
        if type(field) != type([]):
            if unpack:
                return field.value
            return [field.value]
        values = []
        for item in field:
            values.append(item.value)
        return values


    def append_http_headers(self, *args, **kwargs):
        assert not self.__headers_sent
        for key in kwargs:
            self.__http_headers.append((key, kwargs[key]))


    def get_http_headers(self):
        #FIXME: Do we need to check the permission of the caller?
        return self.__http_headers


    def get_i18n(self):
        return gettext


    def get_db(self):
        #FIXME: Check permission of the caller!
        return self.__guard_db.db


    def get_guard_db(self):
        #FIXME: Check permission of the caller!
        return self.__guard_db


    def get_guard(self):
        #FIXME: Check permission of the caller!
        return self.__guard_mod


    def get_integrator(self):
        #FIXME: Check permission of the caller!
        assert self._manager # Api must be associated to the manager first.
        return self._manager


    def get_login(self):
        #FIXME: Check permission of the caller!
        return self.__login


    def set_requested_page(self, page):
        self.__requested_page = page


    def get_requested_page(self):
        return self.__requested_page


    def get_requested_uri(self, *args, **kwargs):
        return get_request_uri(**kwargs)


    def has_permission(self, permission):
        """
        Returns true if the current user has the given permission
        on the current page.
        """
        assert permission is not None
        private = self.__requested_page.get_attribute('private') or False
        if permission == 'view' and not private:
            return True
        user = self.__login.get_current_user()
        if user is None:
            return False
        section = 'content_permissions'
        action  = self.__guard_db.get_action_from_handle(permission, section)
        assert action is not None
        return self.__guard_db.has_permission(user,
                                              action,
                                              self.__requested_page)


    def render(self, filename, *args, **kwargs):
        if not self.__headers_sent:
            self.send_headers()

        #FIXME: Do we need to check the permission of the caller?
        assert filename is not None
        # Find the object that made the API call.
        extension = self.__get_caller()
        assert extension

        # Point dirname to the path of the plugin that made the call.
        classname  = '%s' % extension.__class__
        subdirname = '/'.join(classname.split('.')[:-2])
        dirname    = os.path.join('data/repo/', subdirname)
        plugin_uri = get_mod_rewrite_prevented_uri(dirname)
        web_dir    = get_mod_rewrite_prevented_uri('web')

        # Load and display the template.
        loader = TemplateLoader([dirname])
        tmpl   = loader.load(filename, None, MarkupTemplate)
        print tmpl.generate(plugin_dir  = plugin_uri,
                            web_dir     = web_dir,
                            uri         = get_uri,
                            request_uri = get_request_uri,
                            txt         = gettext,
                            **kwargs).render('xhtml')


    def save_page(self, page):
        #FIXME: Do we need to check the permission of the caller?
        section = self.__guard_mod.ResourceSection('content')
        return self.__guard_db.save_resource(page, section)


if __name__ == '__main__':
    import unittest

    class ExtensionApiTest(unittest.TestCase):
        def runTest(self):
            #FIXME: Implement test.
            pass
            
    testcase = ExtensionApiTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
