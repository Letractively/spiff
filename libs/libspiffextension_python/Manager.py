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

class Manager:
    __no_such_file_error,     \
    __install_error,          \
    __parse_error,            \
    __unmet_dependency_error, \
    __database_error,         \
    __permission_denied_error = range(6)
    
    def  __init__(self, db):
        self.db             = db
        self.__extension_db = DB(self.db)


    def __parse_header(self, filename):
        assert os.path.is_file(filename)
        #FIXME


    def __install_directory(self, dirname):
        assert os.path.is_dir(dirname)
        prefix = os.path.basename(dirname)
        target = mkdtemp('', prefix, dirname)
        if not target: return None
        os.path.copy(dirname, target)
        return target


    def __install_archive(self, filename):
        assert os.path.is_file(filename)
        dirname = os.path.dirname(filename)
        prefix  = os.path.basename(filename).sub('.')
        target  = mkdtemp('', prefix, dirname)
        if not unzip(filename, target):
            return None
        return target


    def add_extension(self, filename, permission_request_func = None):
        """
        Installs the given extension.
        
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
            return __no_such_file_error

        # Install files.
        if os.path.isdir(filename):
            # Copy the directory into the target directory.
            install_dir = self.__install_directory(filename)
        else:
            # Unpack the extension into the target directory.
            install_dir = self.__install_archive(filename)
        if not install_dir:
            return __install_error

        # Read the extension header.
        header = self.__parse_header(install_dir)
        if not header: return __parse_error

        # Check dependencies.
        for context in header['dependencies']:
            for descriptor in header['dependencies']['context']:
                if not __extension_db.has_extension_from_descriptor(descriptor):
                    return __unmet_dependency_error

        # Check whether the extension has permission to listen to the
        # requested events.
        if permission_request_func is not None:
            for callback in header['callbacks']:
                event_uri = callback.get_context()
                permit    = permission_request_func(extension, event_uri)
                if not permit: return __permission_denied_error
            
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
        if not id: return __database_error

        return id


    def remove_extension_from_id(self, id):
        """
        Uninstalls the extension with the given id.

        @type  id: int
        @param id: The id of the extension to remove.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """


    def emit(name):
        #FIXME
        pass
        
