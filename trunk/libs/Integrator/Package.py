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
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Guard     import Resource
from Callback  import Callback
from functions import descriptor_parse

class Package(Resource):
    def __init__(self, name, handle = None, version = '0', **kwargs):
        assert name    is not None
        assert version is not None
        Resource.__init__(self, name, handle)
        self.__dependencies = {}
        self.__signals      = None
        self.__listeners    = None
        self.__parent       = kwargs.get('parent')
        self.__module       = None
        self.set_version(version)


    def set_id(self, id):
        Resource.set_id(self, id)
        if self.__signals is None:
            self.__signals = []
        if self.__listeners is None:
            self.__listeners = []


    def _set_parent(self, parent):
        self.__parent = parent


    def set_author(self, author):
        assert author is not None and author != ''
        self.set_attribute('author', author)


    def get_author(self):
        return self.get_attribute('author')


    def set_description(self, description):
        assert description is not None
        self.set_attribute('description', description)


    def get_description(self):
        return self.get_attribute('description')


    def set_version(self, version):
        assert version is not None and version != ''
        self.set_attribute('version', version)


    def get_version(self):
        return self.get_attribute('version')


    def add_dependency(self, descriptor, context = 'default'):
        assert descriptor is not None and descriptor is not ''
        assert context    is not None and context    is not ''
        #print "Descriptor:", descriptor
        matches = descriptor_parse(descriptor)
        assert matches is not None
        if not self.__dependencies.has_key(context):
            self.__dependencies[context] = [descriptor]
        else:
            self.__dependencies[context].append(descriptor)


    def get_dependency_context_list(self):
        return self.__dependencies.keys()


    def get_dependency_list(self, context = None):
        if context is not None:
            return self.__dependencies[context]
        dependency_list = []
        for context in self.__dependencies:
            dependency_list += self.__dependencies[context]
        return dependency_list


    def add_signal(self, uri):
        """
        Define that this package sends the given signal.
        """
        if self.__signals is None:
            self.__signals = [uri]
            return
        self.__signals.append(uri)


    def get_signal_list(self):
        """
        Returns the list of signals that this package may send.
        """
        if self.__signals is not None:
            return self.__signals
        assert self.__parent is not None
        db             = self.__parent.package_db
        id             = self.get_id()
        self.__signals = db.get_signal_list_from_package_id(id)
        return self.__signals


    def add_listener(self, uri):
        """
        Define that this package listens to the given signal.
        """
        if self.__listeners is None:
            self.__listeners = [uri]
            return
        self.__listeners.append(uri)


    def get_listener_list(self):
        """
        Returns the list of signals to which this package may respond.
        """
        if self.__listeners is not None:
            return self.__listeners
        assert self.__parent is not None
        db               = self.__parent.package_db
        id               = self.get_id()
        self.__listeners = db.get_listener_list_from_package_id(id)
        return self.__listeners


    def get_module_dir(self):
        return 'package' + str(self.get_id())


    def load(self):
        assert self.__parent is not None
        if self.__module is not None:
            return self.__module

        module   = __import__(self.get_module_dir())
        instance = module.Extension(self.__parent.package_api)

        for uri in self.get_listener_list():
            func_name = 'on_' + uri.replace(':', '_').replace('/', '_')
            func     = getattr(instance, func_name)
            listener = Callback(func, uri)
            self.__parent.event_bus.add_listener(listener)

        self.__module = instance
        self.__parent._load_notify(self, instance)
        return self.__module
