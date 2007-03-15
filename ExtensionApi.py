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
from functions       import get_request_uri,gettext
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
        assert kwargs.has_key('guard_mod')
        assert kwargs.has_key('get_data')
        assert kwargs.has_key('post_data')
        Api.__init__(self, guard_db, manager, event_bus)
        self.__login        = Login(guard_db)
        self.__guard_db     = guard_db
        self.__guard_mod    = kwargs['guard_mod']
        self.__get_data     = kwargs['get_data']
        self.__post_data    = kwargs['post_data']
        self.__headers_sent = False


    def __get_caller(self):
        frame = sys._getframe(2)
        try:
            caller = frame.f_locals['self']
        finally:
            del frame
        return caller


    def get_i18n(self):
        return gettext


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


    def send_headers(self, content_type = 'text/html', headers = {}):
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
        tmpl         = loader.load('header.tmpl', None, TextTemplate)
        print tmpl.generate(current_user = current_user,
                            txt          = gettext).render('text')


    def headers_sent(self):
        return self.__headers_sent

        
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

        # Load and display the template.
        loader = TemplateLoader([dirname])
        tmpl   = loader.load(filename, None, MarkupTemplate)
        print tmpl.generate(plugin_dir  = dirname,
                            request_uri = get_request_uri,
                            txt         = gettext,
                            **kwargs).render('xhtml')


if __name__ == '__main__':
    import unittest

    class ExtensionApiTest(unittest.TestCase):
        def runTest(self):
            #FIXME: Implement test.
            pass
            
    testcase = ExtensionApiTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
