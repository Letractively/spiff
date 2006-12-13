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
from Callback import *
from DB       import *
from tempfile import *
import Parser
import os.path
import shutil
import zipfile

class Manager:
    __no_such_file_error,     \
    __install_error,          \
    __parse_error,            \
    __unmet_dependency_error, \
    __database_error,         \
    __permission_denied_error = range(6)
    
    def  __init__(self, acldb):
        self.__extension_db = DB(acldb)
        self.__install_dir  = None

    
    def set_install_dir(self, dirname):
        assert os.path.isdir(dirname)
        self.__install_dir = dirname


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
                os.mkdir(os.path.join(target, name))
            else:
                outfile = open(os.path.join(target, name), 'wb')
                outfile.write(zfobj.read(name))
                outfile.close()
        return target


    def add_extension(self, filename, permission_request_func = None):
        """
        Installs the given extension.
        
        If the extension wants to subscribe to a potentially fancy
        hook (=event bus signal) that requires permission, the given
        permission_request_func() is called to inquire about whether
        permission should be granted. If permission_request_func is not
        specified, the extension is by default granted any requested
        permission.
        
        The permission_request_func() has the following signature:
          permission_request(extension, event_uri)
        where
          extension: is the extension that is to be registered
          uri:       is an URI addressing the event that the extension
                     would like to catch.
        @type  filename: os.path
        @param filename: Path to the file containing the extension.
        @type  permission_request_func: function
        @param permission_request_func: Invoked when requesting permission to
                                        add a new callback.
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

        # Read the extension header.
        class_file = os.path.join(install_dir, 'Extension.py')
        header     = Parser.parse_header(class_file)
        if not header: return self.__parse_error

        # Check dependencies.
        for descriptor in header['runtime_dependency']:
            if not self.__extension_db.get_extension_from_descriptor(descriptor):
                shutil.rmtree(install_dir)
                return self.__unmet_dependency_error

        # Check whether the extension has permission to listen to the
        # requested events.
        if permission_request_func is not None:
            for callback in header['callbacks']:
                event_uri = callback.get_context()
                permit    = permission_request_func(extension, event_uri)
                if not permit:
                    shutil.rmtree(install_dir)
                    return self.__permission_denied_error

        # Create instance (or resource).
        modulename = install_dir.replace('/', '.')
        module     = __import__(modulename)
        extension  = module.Extension(self.__extension_api)

        # Append dependencies.
        for context in header['dependencies']:
            for descriptor in header['dependencies']['context']:
                extension.add_dependency(descriptor, context)

        # Append callbacks.
        for callback in header['callbacks']:
            cb_name   = callback.get_name()
            event_uri = callback.get_context()
            extension.add_listener(cb_name, event_uri)

        # Register the extension in the database, including dependencies and
        # callbacks.
        id = self.__extension_db.register_extension(extension)
        if not id:
            shutil.rmtree(install_dir)
            return self.__database_error

        # Rename the directory so that the id can be used to look the
        # extension up.
        try:
            new_install_dir = os.path.join(self.__install_dir, str(id))
            os.rename(install_dir, new_install_dir)
        except:
            shutil.rmtree(install_dir)
            self.remove_extension_from_id(id)
            return self.__install_error

        return id


    def remove_extension_from_id(self, id):
        """
        Uninstalls the extension with the given id.

        @type  id: int
        @param id: The id of the extension to remove.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        res         = self.__extension_db.unregister_extension_from_id(id)
        install_dir = os.path.join(self.__install_dir, str(id))
        if os.path.isdir(install_dir):
            shutil.rmtree(install_dir)
        return res


    def emit(name):
        #FIXME
        pass


if __name__ == '__main__':
    import unittest
    import MySQLdb
    import libspiffacl_python
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
            auth  = user + ':' + password
            dbn   = 'mysql://' + auth + '@' + host + '/' + db_name
            db    = create_engine(dbn)
            acldb = libspiffacl_python.DB(db)

            # Install dependencies.
            extdb = DB(acldb)
            assert extdb.uninstall()
            assert acldb.uninstall()
            assert acldb.install()
            assert extdb.install()

            # Set up.
            manager  = Manager(acldb)
            manager.set_install_dir('tmp')
            
            # Install first extension.
            filename = 'samples/SpiffExtension'
            id = manager.add_extension(filename)
            print 'Return value:', id
            assert id is not None

            # Install second extension.
            filename = 'samples/HelloWorldExtension.zip'
            id = manager.add_extension(filename)
            print 'Return value:', id
            assert id is not None

            # Remove the extension.
            assert manager.remove_extension_from_id(id)

            # Clean up.
            assert extdb.clear_database()
            assert extdb.uninstall()
            assert acldb.uninstall()
            
    testcase = ManagerTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
