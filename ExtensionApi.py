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
from genshi.template import TextTemplate
from genshi.template import MarkupTemplate


class ExtensionApi(Api):
    def __init__(self, guard_db, manager, event_bus, *args, **kwargs):
        assert guard_db  is not None
        assert manager   is not None
        assert event_bus is not None
        assert kwargs.has_key('requested_page')
        assert kwargs.has_key('guard_mod')
        assert kwargs.has_key('get_data')
        assert kwargs.has_key('post_data')
        Api.__init__(self, guard_db, manager, event_bus)
        self.__login          = Login(guard_db)
        self.__guard_db       = guard_db
        self.__requested_page = kwargs['requested_page']
        self.__guard_mod      = kwargs['guard_mod']
        self.__get_data       = kwargs['get_data']
        self.__post_data      = kwargs['post_data']
        self.__headers_sent   = False
        self.add_listener(self.__send_footer, "spiff:extensions_done")


    def __get_caller(self):
        frame = sys._getframe(2)
        try:
            caller = frame.f_locals['self']
        finally:
            del frame
        return caller


    def get_i18n(self):
        return gettext


    def get_db(self):
        #FIXME: Check permission of the caller!
        return self.__guard_db.db


    def set_requested_page(self, page):
        self.__requested_page = page


    def get_requested_page(self):
        return self.__requested_page


    def get_request_uri(self, *args, **kwargs):
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


    def get_login(self):
        #FIXME: Check permission of the caller!
        return self.__login


    def get_guard_db(self):
        #FIXME: Check permission of the caller!
        return self.__guard_db


    def get_guard(self):
        #FIXME: Check permission of the caller!
        return self.__guard_mod


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


    def send_headers(self,
                     content_type = 'text/html; charset=utf-8',
                     headers = {}):
        if self.__headers_sent:
            return
        # Print the HTTP header.
        print 'Content-Type: %s' % content_type
        for k, v in headers.items():
            print '%s: %s\n' % (k, v)
        print
        self.__headers_sent = True
        
        # Load and display the HTML header.
        current_user = self.__login.get_current_user()
        loader       = TemplateLoader(['web'])
        tmpl1        = loader.load('header.tmpl',  None, TextTemplate)
        tmpl2        = loader.load('header2.tmpl', None, MarkupTemplate)
        web_dir      = get_mod_rewrite_prevented_uri('web')
        print tmpl1.generate(web_dir      = web_dir,
                             current_user = current_user,
                             txt          = gettext).render('text')
        print tmpl2.generate(web_dir      = web_dir,
                             request_uri  = get_request_uri,
                             current_user = current_user,
                             txt          = gettext).render('xhtml')


    def headers_sent(self):
        return self.__headers_sent

        
    def __send_footer(self, args):
        loader  = TemplateLoader(['web'])
        tmpl    = loader.load('footer.tmpl', None, TextTemplate)
        web_dir = get_mod_rewrite_prevented_uri('web')
        print tmpl.generate(web_dir = web_dir,
                            txt     = gettext).render('text')


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

        # Load and display the template.
        loader = TemplateLoader([dirname])
        tmpl   = loader.load(filename, None, MarkupTemplate)
        print tmpl.generate(plugin_dir  = plugin_uri,
                            request_uri = get_request_uri,
                            txt         = gettext,
                            **kwargs).render('xhtml', strip_whitespace = False)


if __name__ == '__main__':
    import unittest

    class ExtensionApiTest(unittest.TestCase):
        def runTest(self):
            #FIXME: Implement test.
            pass
            
    testcase = ExtensionApiTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
