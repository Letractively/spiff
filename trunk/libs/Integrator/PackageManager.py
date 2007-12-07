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
from PackageDB import PackageDB
from Package   import Package
from tempfile  import mkdtemp
from EventBus  import EventBus
from Callback  import Callback
from Parser    import Parser
from Exception import IntegratorException
import os
import os.path
import sys
import shutil
import zipfile

class PackageManager(object):
    def  __init__(self, guard, package_api):
        assert guard       is not None
        assert package_api is not None
        self.package_db      = PackageDB(guard)
        self.package_dir     = None
        self.package_api     = package_api
        self.event_bus       = EventBus()
        self.__package_cache = {}
        package_api.activate(self)


    def __install_directory(self, dirname):
        assert os.path.isdir(dirname)
        prefix = os.path.basename(dirname)
        target = mkdtemp('', prefix, self.package_dir)
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
        target = mkdtemp('', prefix, self.package_dir)

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


    def _load_notify(self, package, module):
        self.__package_cache[module] = package


    def install(self):
        """
        Installs the package manager.
        """
        return self.package_db.install()


    def set_package_dir(self, dirname):
        """
        Defines the directory into which new packages are installed, and
        from which they are loaded.
        @type  dirname: os.path
        @param dirname: The package directory.
        """
        if not os.path.isdir(dirname):
            raise IOError('%s: No such directory' % dirname)
        if dirname in sys.path and self.package_dir in sys.path:
            # This is a little evil. But soo easy.
            sys.path.remove(self.package_dir)
        self.package_dir = dirname
        sys.path.append(self.package_dir)


    def add_package(self, filename):
        """
        Installs the given package.
        Raises an exception if the installation failed.

        @type  filename: string
        @param filename: Path to the file containing the package.
        @rtype:  int
        @return: The package.
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

        # Read the package file.
        class_file = os.path.join(install_dir, 'Extension.xml')
        parser     = Parser()
        try:
            package = parser.parse_file(class_file)
        except:
            shutil.rmtree(install_dir)
            raise IntegratorException('Unable to parse %s' % class_file)
        package._set_parent(self)

        # Check dependencies.
        for descriptor in package.get_dependency_list():
            if not self.package_db.get_package_from_descriptor(descriptor):
                shutil.rmtree(install_dir)
                raise IntegratorException('Unmet dependency: %s' % descriptor)

        # Register the package in the database.
        try:
            result = self.package_db.add_package(package)
            id     = package.get_id()
            assert result is not None
            assert id is not None
        except Exception, e:
            shutil.rmtree(install_dir)
            raise IntegratorException('Database error: %s' % e)

        # Rename the directory so that the id can be used to look the
        # package up.
        try:
            subdir          = package.get_module_dir()
            new_install_dir = os.path.join(self.package_dir, subdir)
            if os.path.exists(new_install_dir):
                shutil.rmtree(new_install_dir)
            os.rename(install_dir, new_install_dir)
        except Exception, e:
            shutil.rmtree(install_dir)
            self.remove_package_from_id(id)
            raise IOError('Unable to copy: %s' % e)

        # Ending up here, the package was properly installed in the target
        # directory. Load it.
        try:
            instance = package.load()
        except:
            print 'Error: Unable to load package (%s).' % package.get_name()
            shutil.rmtree(install_dir)
            self.remove_package_from_id(id)
            raise

        # Check whether the package has an install() method.
        install_func = None
        try:
            install_func = getattr(instance, 'install')
        except:
            pass
        if install_func is None:
            return package

        # Call the install method.
        try:
            install_func()
        except:
            print 'Error in install_func() of %s.' % package.get_name()
            shutil.rmtree(install_dir)
            self.remove_package_from_id(id)
            raise

        return package


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
        list = self.package_db.get_package_list(offset, limit)
        for package in list:
            package._set_parent(self)
        return list


    def get_listeners(self, uri):
        """
        Returns a list of all packages that are subscribed to the signal
        with the given URI.

        @type  uri: string
        @param uri: The URI of the signal.
        @rtype:  list[Package]
        @return: The list of packages.
        """
        # Retrieve a list of all package ids that are listeners.
        id_list = self.package_db.get_listener_id_list_from_uri(uri)
        if len(id_list) == 0:
            return []

        # Retrieve the corresponding packages.
        list = self.package_db.get_package_list(id = id_list)
        for package in list:
            package._set_parent(self)
        return list


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
        package = self.package_db.get_package_from_descriptor(descriptor)
        package._set_parent(self)
        return package


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
        package = self.package_db.get_package_from_name(name)
        package._set_parent(self)
        return package


    def remove_package(self, package):
        """
        Uninstalls the given package.

        @type  id: int
        @param id: The id of the package to remove.
        """
        res     = self.package_db.remove_package_from_id(package.get_id())
        pkg_dir = os.path.join(self.package_dir, package.get_module_dir())
        if os.path.isdir(pkg_dir):
            shutil.rmtree(pkg_dir)


    def remove_package_from_id(self, id):
        """
        Uninstalls the package with the given id.

        @type  id: int
        @param id: The id of the package to remove.
        """
        package = Package('', parent = self)
        package.set_id(id)
        return self.remove_package(package)


    def get_package_from_instance(self, instance):
        return self.__package_cache.get(instance)
