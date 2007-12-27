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
from functions import descriptor_parse, version_is_greater

class Package(Resource):
    """
    Represents a package in the database.
    """
    
    def __init__(self, name, handle = None, version = None, **kwargs):
        """
        You normally shouldn't create an instance yourself; instead, ask
        the PackageManager to do this for you.
        
        @type  name: string
        @param name: The name of the package.
        @type  handle: string
        @param handle: The system name of the package.
        @type  version: string
        @param version: The package version.
        @rtype:  Package
        @return: The new instance.
        """
        assert name is not None
        Resource.__init__(self, name, handle)
        self.__filename     = None
        self.__dependencies = {}
        self.__signals      = []
        self.__listeners    = []
        self.__parent       = kwargs.get('parent')
        self.__module       = None
        if version is not None:
            self.set_version(version)


    def __str__(self):
        """
        Returns a string in the following format: "handle=version",
        where "handle" is replaced by the handle of this package and
        "version" is replaced by the version number.

        @rtype:  string
        @return: The handle and version number.
        """
        return '%s=%s' % (self.get_handle(), self.get_version())


    def dump(self):
        """
        Dumps information regarding the package, such as name, version, author,
        and description, to stdout.
        """
        name    = self.get_name()
        version = self.get_version()
        author  = self.get_author()
        email   = self.get_author_email()
        s  = "Filename:     %s\n"      % self.__filename
        s += "Package:      %s %s\n"   % (name, version)
        s += "Author:       %s <%s>\n" % (author, email)
        s += "Dependencies: %s\n"      % ','.join(self.get_dependency_list())
        print s + self.get_description()


    def _set_parent(self, parent):
        self.__parent = parent


    def matches(self, descriptor):
        """
        Returns True if the given descriptor matches the handle and version of
        this package, False otherwise.

        @type  descriptor: string
        @param descriptor: The description (for example, 'spiff>=0.1').
        @rtype:  boolean
        @return: True if the descriptor matches, False otherwise.
        """
        handle, op, version = descriptor_parse(descriptor)
        if handle != self.get_handle():
            return False
        assert op in ('=', '>=')
        if op == '=' and version != self.get_version():
            return False
        if op == '>=' and version_is_greater(version, self.get_version()):
            return False
        return True


    def _set_filename(self, filename):
        """
        Define the filename of the package.

        @type  filename: string
        @param filename: The name of the file.
        """
        assert filename is not None and filename != ''
        self.__filename = filename


    def get_filename(self):
        """
        Returns the filename of this package.

        @rtype:  string
        @return: The full filename.
        """
        assert self.__filename is not None
        return self.__filename


    def set_author(self, author):
        """
        Define the author of the package.

        @type  author: string
        @param author: The name of the author.
        """
        assert author is not None and author != ''
        self.set_attribute('author', author)


    def get_author(self):
        """
        Returns the name of the author of this package.

        @rtype:  string
        @return: The name of the author.
        """
        return self.get_attribute('author')


    def set_author_email(self, email):
        """
        Define the email address of the author of the package.

        @type  email: string
        @param email: The email address.
        """
        assert email is not None and email != ''
        self.set_attribute('author-email', email)


    def get_author_email(self):
        """
        Returns the email address of the author of this package.

        @rtype:  string
        @return: The email address.
        """
        return self.get_attribute('author-email')


    def set_description(self, description):
        """
        Define a description for the package.

        @type  description: string
        @param description: A description of the package.
        """
        assert description is not None
        self.set_attribute('description', description)


    def get_description(self):
        """
        Returns a human readable description of the content of this package.

        @rtype:  string
        @return: The description.
        """
        return self.get_attribute('description')


    def set_version(self, version):
        """
        Define the version of the package.

        @type  version: string
        @param version: The version and release number.
        """
        assert version is not None and version != ''
        self.set_attribute('version', version)


    def get_version(self):
        """
        Returns the version number of this package.

        @rtype:  string
        @return: The version number.
        """
        version = self.get_attribute('version')
        if version is None:
            return '0'
        return version


    def _add_dependency(self, descriptor, context = 'default'):
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
        """
        This function returns a list of all contexts specified by this
        package.
        Packages may specify multiple "types" of dependencies. For
        example, a package may specify a dependency that is only
        needed at install time, and another dependency that is only
        needed at runtime. In such a case, dependencies are sorted
        into different contexts and may be named "install_time" and
        "runtime". The context is specified in the XML index file of
        a package.

        @rtype:  list[string]
        @return: A list of contexts.
        """
        return self.__dependencies.keys()


    def get_dependency_list(self, context = None):
        """
        Returns a list of all dependencies specified by this package.
        If a context is given, only the dependendencies in this
        context are returned.

        @rtype:  list[string]
        @return: A list of dependency descriptors.
        """
        if context is not None:
            return self.__dependencies[context]
        dependencies = {}
        for context, list in self.__dependencies.iteritems():
            for dependency in list:
                dependencies[dependency] = 1
        return dependencies.keys()


    def _add_signal(self, uri):
        """
        Define that this package sends the given signal.
        """
        if self.__signals is None:
            self.__signals = [uri]
            return
        self.__signals.append(uri)


    def _defer_signal_list(self):
        self.__signals = None


    def get_signal_list(self):
        """
        Returns the list of signals that this package may send.

        @rtype:  list[string]
        @return: A list of signal URIs.
        """
        if self.__signals is not None:
            return self.__signals
        assert self.__parent is not None
        db             = self.__parent.package_db
        id             = self.get_id()
        self.__signals = db.get_signal_list_from_package_id(id)
        return self.__signals


    def _add_listener(self, uri):
        """
        Define that this package listens to the given signal.
        """
        if self.__listeners is None:
            self.__listeners = [uri]
            return
        self.__listeners.append(uri)


    def _defer_listener_list(self):
        self.__listeners = None


    def get_listener_list(self):
        """
        Returns the list of signals to which this package may respond.

        @rtype:  list[string]
        @return: A list of signal URIs.
        """
        if self.__listeners is not None:
            return self.__listeners
        assert self.__parent is not None
        db               = self.__parent.package_db
        id               = self.get_id()
        self.__listeners = db.get_listener_list_from_package_id(id)
        return self.__listeners


    def get_module_dir(self):
        """
        Returns the name of the directory in which this package is
        installed.

        @rtype:  string
        @return: The full directory name.
        """
        return 'package' + str(self.get_id())


    def load(self):
        """
        Imports the package, creates an instance, and returns a reference
        to it. Always returns a reference to the same instance if called
        multiple times.

        @rtype:  object
        @return: The instance of package.
        """
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
