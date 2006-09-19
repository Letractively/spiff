class DB:
    def __init__(self, acldb, section_handle):
        self.__acldb        = acldb
        self.__db           = acldb.db
        self.__table_prefix = ''
        self.__acl_section  = libspiffacl_python.ActionSection(section_handle)
        self.__update_table_names()


    def __update_table_names(self):


    def __version_is_greater(self):


    def install(self):
        #FIXME
        pass


    def clear_database(self):
        return self.acldb.clear_section(self.__acl_section)


    def debug(self, debug = True):
        self.db.debug = debug


    def set_table_prefix(self, prefix):
        self.__table_prefix = prefix
        self.__update_table_names()


    def __has_dependency_link_from_id(self, extension_id, dependency_id):
        assert extension_id  >= 0
        assert dependency_id >= 0

    
    def __add_dependency_link_from_id(self, extension_id, dependency_id):
        assert extension_id  >= 0
        assert dependency_id >= 0


    def __get_dependency_id_list_from_id(self, extension_id):
        assert extension_id >= 0


    def __get_dependency_id_list(self, extension):
        assert extension is not None


    def __get_dependency_list_from_id(self, extension_id):
        assert extension_id >= 0


    def __get_dependency_list(self, extension):
        assert extension is not None


    def check_dependencies(self, extension):
        """
        Checks whether the required dependencies are registered.

        Returns True if all dependencies needed to register the given
        extension are registered, False otherwise.

        @type  extension: Extension
        @param extension: The extension whose dependencies are wanted.
        @rtype:  Boolean
        @return: True if all dependency requirements are met, False otherwise.
        """
        assert extension is not None
        #FIXME
        return True


    def register_extension(self, extension):
        """
        Register an extension.

        Inserts the given Extension into the database.
        The method takes no action if the extension is already registered.

        @type  extension: Extension
        @param extension: The extension to install.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert extension is not None
        #FIXME
        return True


    def unregister_extension_from_id(self, id):
        """
        Removes the given Extension from the database.

        @type  id: int
        @param id: The id of the extension to remove.
        @rtype:  Boolean
        @return: False if the extension did not exist, True otherwise.
        """
        assert extension_id >= 0


    def unregister_extension_from_handle(self, handle):
        """
        Removes the given Extension from the database.

        @type  handle: string
        @param handle: The handle of the extension to remove.
        @rtype:  Boolean
        @return: False if the extension did not exist, True otherwise.
        """
        assert handle is not None


    def unregister_extension(self, extension):
        """
        Removes the given Extension from the database.

        @type  extension: Extension
        @param extension: The extension to remove.
        @rtype:  Boolean
        @return: False if the extension did not exist, True otherwise.
        """
        assert extension is not None


    def get_extension_from_id(self, id):
        """
        Returns the extension with the given id from the database.

        @type  id: int
        @param id: The id of the wanted extension.
        @rtype:  Extension
        @return: The extension on success, None if it does not exist.
        """
        assert id >= 0


    def get_extension_from_handle(self, handle, version):
        """
        Returns the extension with the given handle from the database.

        @type  handle:  string
        @param handle:  The handle of the wanted extension.
        @type  version: string
        @param version: The version number of the wanted extension.
        @rtype:  Extension
        @return: The extension on success, None if none was found.
        """
        assert handle is not None


    def get_extension_from_descriptor(self, descriptor):
        """
        Returns the extension that best matches the given descriptor.

        Looks for all extensions that match the given descriptor and
        returns the one with the highest version number.

        The descriptor is defined as follows:
          [handle][operator][version]
        where
          handle is the handle of the extension.
          operator is one of '>=', '='.
          version is a version number.
        
        Descriptor examples:
          spiff>=0.1
          spiff_forum=1.2.3

        @type  descriptor: string
        @param descriptor: The descriptor as specified above.
        @rtype:  Extension
        @return: The extension on success, None if none was found.
        """
        assert operator is not None


    def get_version_list_from_handle(self, handle):
        """
        Returns a list of all registered versions that have the given
        handle.

        @type  handle:  string
        @param handle:  The handle of the wanted extension versions.
        @rtype:  list[string]
        @return: A list containing version numbers.
        """
        assert handle is not None
