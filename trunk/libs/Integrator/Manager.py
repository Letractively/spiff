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
from Api      import Api
from DB       import *
from tempfile import *
from EventBus import EventBus
from Callback import Callback
from Parser   import Parser
import os
import os.path
import shutil
import zipfile

class Manager:
    __no_such_file_error,     \
    __install_error,          \
    __parse_error,            \
    __unmet_dependency_error, \
    __database_error,         \
    __permission_denied_error = range(-1, -7, -1)
    
    def  __init__(self, guard_db, extension_api):
        assert guard_db      is not None
        assert extension_api is not None
        self.__extension_db    = DB(guard_db)
        self.__extension_api   = extension_api
        self.__install_dir     = None
        self.__extension_cache = {}
        self.event_bus         = EventBus()
        extension_api.activate(self)


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


    def set_extension_dir(self, dirname):
        """
        Defines the directory into which new extensions are installed, and
        from which they are loaded.
        @type  dirname: os.path
        @param dirname: The extension directory.
        """
        assert os.path.isdir(dirname)
        if dirname in sys.path and self.__install_dir in sys.path:
            # This is a little evil. But soo easy.
            sys.path.remove(self.__install_dir)
        self.__install_dir = dirname
        sys.path.append(self.__install_dir)


    def add_extension(self,
                      filename,
                      event_request_func  = None,
                      signal_request_func = None):
        """
        Installs the given extension.
        
        If the extension wants to subscribe to an event bus signal
        that requires permission, the given event_request_func() is
        called to inquire about whether permission should be granted.
        If event_request_func is not specified, the extension is by
        default granted any requested permission.
        
        The event_request_func() has the following signature:
          permission_request(extension_info, event_uri)
        where
          extension_info: is the ExtensionInfo that is to be registered
          uri:            is an URI addressing the event that the extension
                          would like to catch.
        
        If the extension wants to emit an event bus signal
        that requires permission, the given signal_request_func() is
        called to inquire about whether permission should be granted.
        If signal_request_func is not specified, the extension is by
        default granted any requested permission.
        
        The signal_request_func() has the following signature:
          permission_request(extension_info, event_uri)
        where
          extension_info: is the ExtensionInfo that is to be registered
          uri:            is an URI addressing the event that the extension
                          would like to emit.
        @type  filename: os.path
        @param filename: Path to the file containing the extension.
        @type  event_request_func: function
        @param event_request_func: Invoked when requesting permission to
                                   add a new listener.
        @type  signal_request_func: function
        @param signal_request_func: Invoked when requesting permission to
                                    add a new signal.
        @rtype:  int
        @return: The extension id (>=0) if the extension was successfully
                 installed, <0 otherwise.
        """
        if not os.path.exists(filename):
            return self.__no_such_file_error

        # Install files.
        if os.path.isdir(filename):
            # Copy the directory into the target directory.
            install_dir = self.__install_directory(filename)
        else:
            # Unpack the extension into the target directory.
            install_dir = self.__install_archive(filename)
        if not install_dir:
            return self.__install_error

        # Read the extension info.
        class_file = os.path.join(install_dir, 'Extension.xml')
        parser     = Parser()
        parser.parse_file(class_file)
        info = parser.info
        if info is None:
            return self.__parse_error

        # Check dependencies.
        for descriptor in info.get_dependency_list():
            #print "Descriptor:", descriptor
            if not self.__extension_db.get_extension_from_descriptor(descriptor):
                shutil.rmtree(install_dir)
                return self.__unmet_dependency_error

        # Check whether the extension has permission to listen to the
        # requested events.
        if event_request_func is not None:
            for uri in parser.listeners:
                # event_request_func() may modify the signal URI.
                permit = event_request_func(info, uri)
                if not permit:
                    shutil.rmtree(install_dir)
                    return self.__permission_denied_error

        # Check whether the extension has permission to send the
        # requested events.
        if signal_request_func is not None:
            for uri in parser.signals:
                # signal_request_func() may modify the signal URI.
                permit = signal_request_func(info, uri)
                if not permit:
                    shutil.rmtree(install_dir)
                    return self.__permission_denied_error
                #FIXME: Store list of permitted signals in the database.

        # Register the extension in the database, including dependencies.
        result = self.__extension_db.register_extension(info)
        if not result:
            shutil.rmtree(install_dir)
            return self.__database_error
        id = info.get_id()
        assert id > 0

        for uri in parser.listeners:
            try:
                self.__extension_db.link_extension_id_to_callback(id, uri)
            except:
                shutil.rmtree(install_dir)
                return self.__database_error

        # Rename the directory so that the id can be used to look the
        # extension up.
        try:
            subdir          = 'extension' + str(id)
            new_install_dir = os.path.join(self.__install_dir, subdir)
            if os.path.exists(new_install_dir):
                shutil.rmtree(new_install_dir)
            os.rename(install_dir, new_install_dir)
        except:
            shutil.rmtree(install_dir)
            self.remove_extension_from_id(id)
            return self.__install_error

        return info.get_id()


    def get_extension_info_list(self, offset = 0, limit = 0):
        """
        Returns a list of all installed extensions.

        @type  offset: int
        @param offset: The number of extensions to skip.
        @type  limit: int
        @param limit: The maximum number of extensions returned.
        @rtype:  list[ExtensionInfo]
        @return: The list of extensions.
        """
        return self.__extension_db.get_extension_list(offset, limit)


    def get_extension_info_from_descriptor(self, descriptor):
        """
        Returns the ExtensionInfo object that matches the given descriptor.
        If multiple versions match, the most recent version is returned.

        @type  name: string
        @param name: A descriptor (e.g. "my_extension>=1.0").
        @rtype:  ExtensionInfo
        @return: The ExtensionInfo, or None if none was found.
        """
        assert descriptor is not None
        return self.__extension_db.get_extension_from_descriptor(descriptor)


    def get_extension_info_from_name(self, name):
        """
        Returns the ExtensionInfo object with the given name. If multiple
        versions exist, the most recent version is returned.

        @type  name: string
        @param name: The name of the extension.
        @rtype:  ExtensionInfo
        @return: The ExtensionInfo, or None if none was found.
        """
        assert name is not None
        return self.__extension_db.get_extension_from_name(name)


    def remove_extension_from_id(self, id):
        """
        Uninstalls the extension with the given id.

        @type  id: int
        @param id: The id of the extension to remove.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        res         = self.__extension_db.unregister_extension_from_id(id)
        subdir      = 'extension' + str(id)
        install_dir = os.path.join(self.__install_dir, subdir)
        if os.path.isdir(install_dir):
            shutil.rmtree(install_dir)
        return res


    def load_extension_from_id(self, id):
        assert id > 0
        
        # Use cache if applicable.
        if self.__extension_cache.has_key(str(id)):
            return self.__extension_cache[str(id)]

        # Create instance (or resource).
        subdir     = 'extension' + str(id)
        modulename = subdir.replace('/', '.')
        try:
            module    = __import__(modulename)
            extension = module.Extension(self.__extension_api)
        except:
            print 'Ooops... a broken extension.'
            raise

        # Connect signals.
        uri_list = self.__extension_db.get_callback_list_from_extension_id(id)
        assert uri_list is not None
        for uri in uri_list:
            func_name = 'on_' + uri.replace(':', '_').replace('/', '_')
            func      = getattr(extension, func_name)
            callback  = Callback(func, uri)
            self.event_bus.add_listener(callback)

        # Store in cache and return.
        self.__extension_cache[str(id)] = extension
        return extension


    def load_extension_from_descriptor(self, descriptor):
        assert descriptor is not None

        # Look the extension info up in the db.
        db   = self.__extension_db
        info = db.get_extension_from_descriptor(descriptor)
        if info is None:
            return None
        return self.load_extension_from_id(info.get_id())


    def load_extension_from_name(self, name):
        assert name is not None

        # Look the extension info up in the db.
        db   = self.__extension_db
        info = db.get_extension_from_name(name)
        print name, info

        if info is None:
            return None
        return self.load_extension_from_id(info.get_id())


    def load_extension_from_event(self, uri):
        list = self.__extension_db.get_extension_id_list_from_callback(uri)
        for id in list:
            self.load_extension_from_id(id)


if __name__ == '__main__':
    import unittest
    import MySQLdb
    import Guard
    from Api          import Api
    from ConfigParser import RawConfigParser

    class ManagerTest(unittest.TestCase):
        def runTest(self):
            # Read config.
            cfg = RawConfigParser()
            cfg.read('unit_test.cfg')
            host     = cfg.get('database', 'host')
            db_name  = cfg.get('database', 'db_name')
            user     = cfg.get('database', 'user')
            password = cfg.get('database', 'password')

            # Connect to MySQL.
            auth     = user + ':' + password
            dbn      = 'mysql://' + auth + '@' + host + '/' + db_name
            db       = create_engine(dbn)
            guard_db = Guard.DB(db)

            # Install dependencies.
            extdb = DB(guard_db)
            assert extdb.uninstall()
            assert guard_db.uninstall()
            assert guard_db.install()
            assert extdb.install()

            # Set up.
            api     = Api()
            manager = Manager(guard_db, api)
            manager.set_extension_dir('tmp')
            
            # Install first extension.
            filename = 'samples/SpiffExtension'
            id1      = manager.add_extension(filename)
            assert id1 > 0

            # Install second extension.
            filename = 'samples/HelloWorldExtension'
            id2      = manager.add_extension(filename)
            assert id2 > 0

            # Remove the extension.
            assert manager.remove_extension_from_id(id2)
            assert manager.remove_extension_from_id(id1)

            # Clean up.
            assert extdb.clear_database()
            assert extdb.uninstall()
            assert guard_db.uninstall()
            
    testcase = ManagerTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
