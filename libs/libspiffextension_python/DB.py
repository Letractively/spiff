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
sys.path.append('..')
from sqlalchemy import *

class DB:
    def __init__(self, acldb, section_handle = 'extensions'):
        self.db            = acldb.db
        self._acldb        = acldb
        self._table_prefix = ''
        self._table_map    = {}
        self._table_list   = []
        self._acl_section  = libspiffacl_python.ResourceSection(section_handle)
        self.__update_table_names()


    def __add_table(self, table):
        self._table_list.append(table)
        self._table_map[table.name] = table


    def __update_table_names(self):
        metadata  = self._acldb.db_metadata
        pfx       = self._table_prefix
        acldb_pfx = self._acldb.get_table_prefix()
        self.__add_table(Table(pfx + 'extension_dependency', metadata,
            Column('id',                  Integer,    primary_key = True),
            Column('extension_id',        Integer,    index = True),
            Column('dependency_handle',   String(20), index = True),
            Column('dependency_operator', String(3),  index = True),
            Column('dependency_version',  String(20), index = True),
            ForeignKeyConstraint(['extension_id'],
                                 [acldb_pfx + 'resource.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'extension_dependency_map', metadata,
            Column('extension_id',  Integer, index = True),
            Column('dependency_id', Integer, index = True),
            ForeignKeyConstraint(['extension_id'],
                                 [acldb_pfx + 'resource.id'],
                                 ondelete = 'CASCADE'),
            ForeignKeyConstraint(['dependency_id'],
                                 [acldb_pfx + 'resource.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'extension_callback', metadata,
            Column('id',           Integer,     primary_key = True),
            Column('extension_id', Integer,     index = True),
            Column('name',         String(200)),
            Column('event_uri',    String(255), index = True),
            ForeignKeyConstraint(['extension_id'],
                                 [acldb_pfx + 'resource.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))


    def debug(self, debug = True):
        self.db.debug = debug


    def set_table_prefix(self, prefix):
        self._table_prefix = prefix
        self.__update_table_names()


    def install(self):
        """
        Installs (or upgrades) database tables.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        for table in self._table_list:
            table.create(checkfirst = True)
        return True


    def uninstall(self):
        """
        Drops all tables from the database. Use with care.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        for table in self._table_list[::-1]:
            table.drop(checkfirst = True)
        return True


    def clear_database(self):
        """
        Drops the content of any database table used by this library.
        Use with care.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        return self._acldb.delete_resource_section(self._acl_section)


    def __has_dependency_link_from_id(self, extension_id, dependency_id):
        assert extension_id  >= 0
        assert dependency_id >= 0
        table  = self._table_map['extension_dependency_map']
        query  = select([table.c.extension_id],
                        and_(table.c.extension_id  == extension_id,
                             table.c.dependency_id == dependency_id),
                        from_obj = [table])
        result = query.execute()
        assert result is not None
        row = result.fetchone()
        if not row: return False
        return True

    
    def __add_dependency_link_from_id(self, extension_id, dependency_id):
        assert extension_id  >= 0
        assert dependency_id >= 0
        table  = self._table_map['extension_dependency_map']
        query  = table.insert()
        result = query.execute(extension_id  = extension_id,
                               dependency_id = dependency_id)
        assert result is not None


    def __get_dependency_id_list_from_id(self, extension_id):
        assert extension_id >= 0
        table  = self._table_map['extension_dependency_map']
        query  = select([table.c.dependency_id],
                        table.c.extension_id == extension_id,
                        from_obj = [table])
        result = query.execute()
        assert result is not None

        dependency_id_list = []
        for row in result:
            dependency_id_list.append(row[table.c.extension_id])
        return dependency_id_list


    def __get_dependency_id_list(self, extension):
        assert extension is not None
        return self.__get_dependency_id_list_from_id(extension.get_id())


    def __get_dependency_list_from_id(self, extension_id):
        assert extension_id >= 0
        id_list = self.__get_dependency_id_list_from_id(extension_id)
        return self._acldb.get_resource_list_from_id_list(id_list)

        dependency_id_list = []
        for row in result:
            dependency_id_list.append(row[table.c.extension_id])
        return dependency_id_list


    def __get_dependency_list(self, extension):
        assert extension is not None
        return self.__get_dependency_list_from_id(extension.get_id())


    def __load_dependency_list(self, extension):
        assert extension is not None
        list = self.__get_dependency_list(extension)
        for dependency in list:
            extension.add_dependency(dependency.get_handle())
        return True


    def check_dependencies(self, extension):
        """
        Checks whether all required dependencies are registered.

        Returns True if all dependencies needed to register the given
        extension are registered, False otherwise.

        @type  extension: Extension
        @param extension: The extension whose dependencies will be checked.
        @rtype:  Boolean
        @return: True if all dependency requirements are met, False otherwise.
        """
        assert extension is not None
        dependency_list = extension.get_dependency_list()
        for descriptor in dependency_list:
            if not self.get_extension_from_descriptor(descriptor):
                return False
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

        # Check whether the extension is already registered.
        if self.get_extension_from_handle(extension.get_handle(),
                                          extension.get_version()):
            return True

        # Make sure that all dependencies are registered.
        assert self.check_dependencies(extension)

        # Start transaction.
        connection  = self.db.connect()
        transaction = connection.begin()

        # Create a group that holds all versions of the extension.
        handle   = extension.get_handle()
        s_handle = self._acl_section.get_handle()
        if self._acldb.get_resource_from_handle(handle, s_handle) is None:
            parent = ResourceGroup(extension.get_name(), handle)
            self._acldb.add_resource(None, parent, self._acl_section)
        else:
            parent = self._acldb.get_resource_from_handle(handle, s_handle)

        # Insert the extension into the ACL resource table.
        old_handle = extension.get_handle()
        new_handle = old_handle + extension.get_version()
        handle     = make_handle_from_string(new_handle)
        extension.set_handle(handle)
        self._acldb.add_resource(parent.get_id(), extension, self._acl_section)
        extension.set_handle(old_handle)
        
        # Walk through all requested dependencies.
        for descriptor in extension.get_dependency_list():
            matches = descriptor_parse(descriptor)
            assert matches is not None
            dependency_handle   = matches.group(1)
            dependency_operator = matches.group(2)
            dependency_version  = matches.group(3)
            if dependency_operator is None:
                dependency_operator = '>='
                dependency_version  = 0

            # Add the dependency request into the database.
            table  = self._table_map['extension_dependency_map']
            query  = table.insert()
            result = query.execute(extension_id        = extension.get_id(),
                                   dependency_handle   = dependency_handle,
                                   dependency_operator = dependency_operator,
                                   dependency_version  = dependency_version)
            assert result is not None

            # And link the extension with the best matching dependency.
            best = self.get_extension_from_descriptor(descriptor)

            # Retrieve a list of all dependencies of that dependency.
            dependency_id = dependency.get_id()
            list          = self.get_dependency_id_list_from_id(dependency_id)
            list.append(dependency_id)

            # Add a link to all of the dependencies.
            for id in list:
                self.__add_dependency_link_from_id(extension.get_id(), id)

        # Walk through all extensions that currently depend on another
        # version of the recently registered extension.
        handle  = extension.get_handle()
        version = extension.get_version()
        table   = self._table_map['extension_dependency']
        query   = select([table],
                         and_(table.c.dependency_handle  == handle,
                              table.c.dependency_version == version),
                        from_obj = [table])
        result = query.execute()
        assert result is not None
        for row in result:
            dep_handle   = handle
            dep_operator = row[table.c.dependency_operator]
            dep_version  = row[table.c.dependency_version]
            dependency   = self.get_extension_from_descriptor(dep_handle,
                                                              dep_operator,
                                                              dep_version)
            
            # No need to do anything if the registered link is already the
            # best one.
            dep_id = dependency.get_id()
            if self.__has_dependency_link_from_id(extension.get_id(), dep_id):
                continue

            # Delete the old dependency links.
            self.__delete_dependency_link_from_id(extension.get_id())

            # Retrieve a list of all dependencies of that dependency.
            dep_list = self.__get_dependency_id_list_from_id(dep_id)
            dep_list.append(dep_id)

            for id in dep_list:
                self.__add_dependency_link_from_id(extension.get_id(), dep_id)

        # Transaction finish.
        transaction.commit()
        connection.close()
        return True


    def unregister_extension_from_id(self, id):
        """
        Removes the given Extension from the database. Warning: Also removes
        any extension that requires the given Extension.

        @type  id: int
        @param id: The id of the extension to remove.
        @rtype:  Boolean
        @return: False if the extension did not exist, True otherwise.
        """
        assert extension_id >= 0
        dependency_list = self.get_dependency_id_list_from_id(id)
        self._acldb.delete_resource_from_id(id)
        # Unregister all extensions that require this extension.
        for dependency_id in dependency_list:
            self._acldb.delete_resource_from_id(id)
        return True


    def unregister_extension_from_handle(self, handle):
        """
        Removes the given Extension from the database.

        @type  handle: string
        @param handle: The handle of the extension to remove.
        @rtype:  Boolean
        @return: False if the extension did not exist, True otherwise.
        """
        assert handle is not None
        extension = self.get_extension_from_handle(handle)
        return self.unregister_extension_from_id(extension.get_id())


    def unregister_extension(self, extension):
        """
        Removes the given Extension from the database.

        @type  extension: Extension
        @param extension: The extension to remove.
        @rtype:  Boolean
        @return: False if the extension did not exist, True otherwise.
        """
        assert extension is not None
        self.unregister_extension_from_id(extension.get_id())
        return True


    def get_extension_from_id(self, id):
        """
        Returns the extension with the given id from the database.

        @type  id: int
        @param id: The id of the wanted extension.
        @rtype:  Extension
        @return: The extension on success, None if it does not exist.
        """
        assert id >= 0
        extension = db.get_resource_from_id(id, 'Extension')
        if extension is None:
            return None
        self.__load_dependency_list(extension)
        return extension


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
        assert handle  is not None
        assert version is not None
        version_handle = make_handle_from_string(handle + version)
        section_handle = self._acl_section.get_handle()
        extension      = db.get_resource_from_handle(version_handle,
                                                     section_handle,
                                                     'Extension')
        if extension is None:
            return None
        extension.set_handle(handle)
        self.__load_dependency_list(extension)
        return extension


    def get_extension_from_descriptor(self, descriptor):
        """
        Returns the extension that best matches the given descriptor.

        Looks for all extensions that match the given descriptor and
        returns the one with the highest version number.

        The descriptor is defined as follows:
          [handle][descriptor][version]
        where
          handle     is the handle of the extension.
          descriptor is one of '>=', '='.
          version    is a version number.
        
        Descriptor examples:
          spiff>=0.1
          spiff_forum=1.2.3

        @type  descriptor: string
        @param descriptor: The descriptor as specified above.
        @rtype:  Extension
        @return: The extension on success, None if none was found.
        """
        assert descriptor is not None
        matches = descriptor_parse(descriptor)
        assert matches is not None
        handle   = matches.group(1)
        operator = matches.group(2)
        version  = matches.group(3)
        if operator == '=':
            return self.get_extension_from_handle(handle, version)

        # Ending up here, the operator is '>='.
        # Select the dependency with the version number that
        # matches the version requirement.
        version_list = self.get_version_list_from_handle(handle)
        best_version = '0'
        for cur_version in version_list:
            if version_is_greater(version, cur_version):
                continue
            if version_is_greater(cur_version, best_version):
                best_version = cur_version

        if best_version == '0':
            return None
        return self.get_extension_from_handle(handle, best_version)


    def get_version_list_from_handle(self, handle):
        """
        Returns a list of all registered versions that have the given
        handle.

        @type  handle: string
        @param handle: The handle of the wanted extension versions.
        @rtype:  list[string]
        @return: A list containing version numbers.
        """
        assert handle is not None
        parent = self._acldb.get_resource_from_handle(handle)
        return self._acldb.get_resource_children(parent, 'Extension')


    def link_extension_to_callback(self, extension_id, callback):
        """
        Associates the given extension with the given callback.

        @type  extension_id: int
        @param extension_id: The id of the extension to associate.
        @type  callback: Callback
        @param callback: The callback to associate.
        @rtype:  int
        @return: The id of the callback, or <0 if an error occured.
        """
        assert extension_id >= 0
        assert callback is not None
        
        table  = self._table_map['extension_callback']
        query  = table.insert()
        result = query.execute(extension_id  = extension_id,
                               callback_name = callback.get_name(),
                               event_uri     = callback.get_event_uri())
        assert result is not None
        return self.db.last_insert_id


    def get_extension_id_list_from_callback(self, callback):
        """
        Returns a list of all extensions that are associated with the given
        callback.

        @type  callback: Callback
        @param callback: The callback to look for.
        @rtype:  list[int]
        @return: A list containing all associated extension ids, None on error.
        """
        assert callback is not None
        
        table  = self._table_map['extension_callback']
        query  = select([table.c.extension_id],
                        and_(table.c.name      == callback.get_name(),
                             table.c.event_uri == callback.get_event_uri()),
                        from_obj = [table])
        result = query.execute()
        assert result is not None

        extension_id_list = []
        for row in result:
            extension_id_list.append(row[table.c.extension_id])
        return extension_id_list


if __name__ == '__main__':
    import unittest
    import MySQLdb
    import libspiffacl_python
    from ConfigParser import RawConfigParser

    class ExtensionDBTest(unittest.TestCase):
        def test_with_db(self, acldb):
            assert acldb is not None

            # Install.
            db = DB(acldb)
            assert db.uninstall()
            assert acldb.uninstall()
            assert acldb.install()
            assert db.install()

            # Clean up.
            assert db.clear_database()
            assert db.uninstall()


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
            self.test_with_db(acldb)

    testcase = ExtensionDBTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
