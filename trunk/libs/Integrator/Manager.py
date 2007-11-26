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
from DB        import *
from tempfile  import *
from EventBus  import EventBus
from Callback  import Callback
from Parser    import Parser
from Exception import IntegratorException
import os
import os.path
import shutil
import zipfile

class Manager:
    def  __init__(self, guard_db, package_api):
        assert guard_db      is not None
        assert package_api is not None
        self.__package_db    = DB(guard_db)
        self.__package_api   = package_api
        self.__install_dir   = None
        self.__package_cache = {}
        self.event_bus       = EventBus()
        package_api.activate(self)


    def __install_directory(self, dirname):
        assert os.path.isdir(dirname)
        prefix = os.path.basename(dirname)
        target = mkdtemp('', prefix, self.__install_dir)
        if not target: return None
        for item in os.listdir(dirname):
            src = os.path.join(dirname, item)
            if os.path.isdir(src):
                shutil.copytree(src, os.path.join(target, item))
            else:
                shutil.copy(src, target)
                os.chmod(target, 0755)
        return target


    def __install_archive(self, filename):
        assert os.path.isfile(filename)
        # Create a temporary directory.
        prefix = os.path.basename(filename)
        target = mkdtemp('', prefix, self.__install_dir)

        # Unzip into the directory.
        zfobj = zipfile.ZipFile(filename)
        if zfobj is None:
            return None
        for name in zfobj.namelist():
            if name.endswith('/'):
                dest = os.path.join(target, name)
                os.mkdir(dest)
                os.chmod(dest, 0755)
            else:
                outfile = open(os.path.join(target, name), 'wb')
                outfile.write(zfobj.read(name))
                outfile.close()
        return target


    def set_package_dir(self, dirname):
        """
        Defines the directory into which new packages are installed, and
        from which they are loaded.
        @type  dirname: os.path
        @param dirname: The package directory.
        """
        if not os.path.isdir(dirname):
            raise IOError('%s: No such directory' % dirname)
        if dirname in sys.path and self.__install_dir in sys.path:
            # This is a little evil. But soo easy.
            sys.path.remove(self.__install_dir)
        self.__install_dir = dirname
        sys.path.append(self.__install_dir)


    def add_package(self,
                    filename,
                    event_request_func  = None,
                    signal_request_func = None):
        """
        Installs the given package.
        
        If the package wants to subscribe to an event bus signal
        that requires permission, the given event_request_func() is
        called to inquire about whether permission should be granted.
        If event_request_func is not specified, the package is by
        default granted any requested permission.
        
        The event_request_func() has the following signature:
          permission_request(package_package, event_uri)
        where
          package_package: is the Package that is to be registered
          uri:            is an URI addressing the event that the package
                          would like to catch.
        
        If the package wants to emit an event bus signal
        that requires permission, the given signal_request_func() is
        called to inquire about whether permission should be granted.
        If signal_request_func is not specified, the package is by
        default granted any requested permission.
        
        The signal_request_func() has the following signature:
          permission_request(package_package, event_uri)
        where
          package_package: is the Package that is to be registered
          uri:            is an URI addressing the event that the package
                          would like to emit.
        @type  filename: os.path
        @param filename: Path to the file containing the package.
        @type  event_request_func: function
        @param event_request_func: Invoked when requesting permission to
                                   add a new listener.
        @type  signal_request_func: function
        @param signal_request_func: Invoked when requesting permission to
                                    add a new signal.
        @rtype:  int
        @return: The package id (>=0) if the package was successfully
                 installed, <0 otherwise.
        """
        if not os.path.exists(filename):
            raise IOError('%s: No such file or direcory' % filename)

        # Install files.
        if os.path.isdir(filename):
            # Copy the directory into the target directory.
            install_dir = self.__install_directory(filename)
        else:
            # Unpack the package into the target directory.
            install_dir = self.__install_archive(filename)
        if not install_dir:
            raise IntegratorException('Unable to copy or unpack %s' % filename)

        # Read the package package.
        class_file = os.path.join(install_dir, 'Extension.xml')
        parser     = Parser()
        parser.parse_file(class_file)
        package    = parser.package
        if package is None:
            raise IntegratorException('Unable to parse %s' % class_file)

        # Check dependencies.
        for descriptor in package.get_dependency_list():
            #print "Descriptor:", descriptor
            if not self.__package_db.get_package_from_descriptor(descriptor):
                shutil.rmtree(install_dir)
                raise IntegratorException('Unmet dependency: %s' % descriptor)

        # Check whether the package has permission to listen to the
        # requested events.
        if event_request_func is not None:
            for uri in parser.listeners:
                # event_request_func() may modify the signal URI.
                permit = event_request_func(package, uri)
                if not permit:
                    shutil.rmtree(install_dir)
                    raise IntegratorException('Listening on %s denied' % uri)

        # Check whether the package has permission to send the
        # requested events.
        if signal_request_func is not None:
            for uri in parser.signals:
                # signal_request_func() may modify the signal URI.
                permit = signal_request_func(package, uri)
                if not permit:
                    shutil.rmtree(install_dir)
                    raise IntegratorException('Permission to %s denied' % uri)
                #FIXME: Store list of permitted signals in the database.

        # Register the package in the database, including dependencies.
        result = self.__package_db.register_package(package)
        if not result:
            shutil.rmtree(install_dir)
            raise IntegratorException('DB error: register_package() failed')
        id = package.get_id()
        assert id > 0

        for uri in parser.listeners:
            try:
                self.__package_db.link_package_id_to_callback(id, uri)
            except:
                shutil.rmtree(install_dir)
                raise IntegratorException('Database error: %s' % e)

        # Rename the directory so that the id can be used to look the
        # package up.
        try:
            subdir          = 'package' + str(id)
            new_install_dir = os.path.join(self.__install_dir, subdir)
            if os.path.exists(new_install_dir):
                shutil.rmtree(new_install_dir)
            os.rename(install_dir, new_install_dir)
        except:
            shutil.rmtree(install_dir)
            self.remove_package_from_id(id)
            raise IOError('Unable to copy: %s' % e)

        # Ending up here, the package was properly installed in the target
        # directory. Load it.
        try:
            instance = self.load_package_from_id(id)
        except:
            print 'Error: Unable to load package (%s).' % package.get_name()
            raise

        # Call it's install method.
        install_func = None
        try:
            install_func = getattr(instance, 'install')
        except:
            pass
        if install_func is not None:
            if not install_func():
                msg = 'install_func() of %s returned False' % package.get_name()
                raise IntegratorException(msg)

        return package.get_id()


    def get_package_list(self, offset = 0, limit = 0):
        """
        Returns a list of all installed packages.

        @type  offset: int
        @param offset: The number of packages to skip.
        @type  limit: int
        @param limit: The maximum number of packages returned.
        @rtype:  list[Package]
        @return: The list of packages.
        """
        return self.__package_db.get_package_list(offset, limit)


    def get_package_from_descriptor(self, descriptor):
        """
        Returns the Package object that matches the given descriptor.
        If multiple versions match, the most recent version is returned.

        @type  name: string
        @param name: A descriptor (e.g. "my_package>=1.0").
        @rtype:  Package
        @return: The Package, or None if none was found.
        """
        assert descriptor is not None
        return self.__package_db.get_package_from_descriptor(descriptor)


    def get_package_from_name(self, name):
        """
        Returns the Package object with the given name. If multiple
        versions exist, the most recent version is returned.

        @type  name: string
        @param name: The name of the package.
        @rtype:  Package
        @return: The Package, or None if none was found.
        """
        assert name is not None
        return self.__package_db.get_package_from_name(name)


    def remove_package_from_id(self, id):
        """
        Uninstalls the package with the given id.

        @type  id: int
        @param id: The id of the package to remove.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        res         = self.__package_db.unregister_package_from_id(id)
        subdir      = 'package' + str(id)
        install_dir = os.path.join(self.__install_dir, subdir)
        if os.path.isdir(install_dir):
            shutil.rmtree(install_dir)
        return res


    def load_package_from_id(self, id):
        assert id > 0
        
        # Use cache if applicable.
        if self.__package_cache.has_key(str(id)):
            return self.__package_cache[str(id)]

        # Create instance (or resource).
        subdir     = 'package' + str(id)
        modulename = subdir.replace('/', '.')

        # The following may throw an exception if the package is broken.
        module   = __import__(modulename)
        instance = module.Extension(self.__package_api)

        # Connect signals.
        uri_list = self.__package_db.get_callback_list_from_package_id(id)
        assert uri_list is not None
        for uri in uri_list:
            func_name = 'on_' + uri.replace(':', '_').replace('/', '_')
            func      = getattr(instance, func_name)
            callback  = Callback(func, uri)
            self.event_bus.add_listener(callback)

        # Store in cache and return.
        self.__package_cache[str(id)] = instance
        return instance


    def load_package_from_descriptor(self, descriptor):
        assert descriptor is not None

        # Look the package package up in the db.
        db   = self.__package_db
        package = db.get_package_from_descriptor(descriptor)
        if package is None:
            return None
        return self.load_package_from_id(package.get_id())


    def load_package_from_name(self, name):
        assert name is not None

        # Look the package package up in the db.
        db   = self.__package_db
        package = db.get_package_from_name(name)
        print name, package

        if package is None:
            return None
        return self.load_package_from_id(package.get_id())


    def load_package_from_event(self, uri):
        list = self.__package_db.get_package_id_list_from_callback(uri)
        for id in list:
            self.load_package_from_id(id)
