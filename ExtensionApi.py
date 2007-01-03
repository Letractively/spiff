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
from Integrator      import Api
from Cookie          import SimpleCookie
from genshi.template import TemplateLoader
from genshi.template import MarkupTemplate

class ExtensionApi(Api):
    def __init__(self, manager, event_bus, *args, **kwargs):
        assert manager             is not None
        assert event_bus           is not None
        assert kwargs['guard']     is not None
        assert kwargs['form_data'] is not None
        Api.__init__(self, manager, event_bus)
        self.__guard        = kwargs['guard']
        self.__form_data    = kwargs['form_data']
        self.__headers_sent = False


    def __get_caller(self):
        frame = sys._getframe(2)
        try:
            caller = frame.f_locals['self']
        finally:
            del frame
        return caller


    def get_guard(self):
        #FIXME: Check permission of the caller!
        return self.__guard


    def get_form_value(self, name):
        #FIXME: Do we need to check the permission of the caller?
        if not self.__form_data.has_key(name):
            return None
        return self.__form_data[name].value


    def send_headers(self, content_type = 'text/html', headers = {}):
        if self.__headers_sent:
            return
        print 'Content-Type: %s' % content_type
        for k, v in headers.items():
            print '%s: %s\n' % (k, v)
        print
        self.__headers_sent = True


    def headers_sent(self):
        return self.__headers_sent

        
    def render(self, filename, *args, **kwargs):
        #FIXME: Do we need to check the permission of the caller?
        assert filename is not None
        # Find the object that made the API call.
        extension = self.__get_caller()
        assert extension
        # Set dirname to plugin path.
        classname  = '%s' % extension.__class__
        subdirname = '/'.join(classname.split('.')[:-2])
        dirname    = os.path.join('data/repo/', subdirname)
        loader     = TemplateLoader([dirname])
        # Load and display the template.
        tmpl       = loader.load(filename, None, MarkupTemplate)
        print tmpl.generate(**kwargs)


if __name__ == '__main__':
    import unittest

    class ExtensionApiTest(unittest.TestCase):
        def runTest(self):
            #FIXME: Implement test.
            pass
            
    testcase = ExtensionApiTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)