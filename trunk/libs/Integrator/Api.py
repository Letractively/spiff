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
import os, sys
from Callback import Callback
from Cookie import SimpleCookie
from genshi.template import TemplateLoader
from genshi.template import MarkupTemplate

class Api:
    def __init__(self, manager, acldb, event_bus, form_data):
        assert manager   is not None
        assert acldb     is not None
        assert event_bus is not None
        assert form_data is not None
        self.__manager   = manager
        self.__acldb     = acldb
        self.__event_bus = event_bus
        self.__form_data = form_data


    def __get_caller(self):
        frame = sys._getframe(2)
        try:
            caller = frame.f_locals['self']
        finally:
            del frame
        return caller


    def get_acldb(self):
        #FIXME: Check permission of the caller!
        return self.__acldb


    #FIXME: This does not belong here. Integrator should rather provide
    #a way for clients to register attributes and methods to the plugin Api.
    def get_form_value(self, name):
        if not self.__form_data.has_key(name):
            return None
        return self.__form_data[name].value


    def add_listener(self, func, uri = None):
        #FIXME: Check uri syntax
        #FIXME: Check permissions!
        callback = Callback(func, uri)
        return self.__event_bus.add_listener(callback)

        
    def __emit(self, uri, args, synchronous):
        #FIXME: Check uri syntax
        #FIXME: Check signal permissions!
        self.__manager.load_extension_from_event(uri)
        if synchronous:
            self.__event_bus.emit_sync(uri, args)
        else:
            self.__event_bus.emit(uri, args)


    def emit(self, uri, args = None):
        return self.__emit(uri, args, False)


    def emit_sync(self, uri, args = None):
        return self.__emit(uri, args, True)


    def render(self, filename, *args, **kwargs):
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

    class ApiTest(unittest.TestCase):
        def runTest(self):
            #FIXME: Implement test.
            pass
            
    testcase = ApiTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
