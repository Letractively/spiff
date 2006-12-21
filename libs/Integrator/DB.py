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
from sqlalchemy import *

from ExtensionInfo   import ExtensionInfo
from Callback        import Callback
from Guard.functions import make_handle_from_string
from Guard           import *
from functions       import *

class DB:
    def __init__(self, acldb, section_handle = 'extensions'):
        self.db                  = acldb.db
        self._acldb              = acldb
        self._table_prefix       = ''
        self._table_map          = {}
        self._table_list         = []
        self._acl_section_handle = section_handle
        self._acl_section        = None
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
            useexisting = True,
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
            useexisting = True,
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'extension_callback', metadata,
            Column('id',           Integer,     primary_key = True),
            Column('extension_id', Integer,     index = True),
            #Column('name',         String(200)),
            Column('event_uri',    String(255), index = True),
            ForeignKeyConstraint(['extension_id'],
                                 [acldb_pfx + 'resource.id'],
                                 ondelete = 'CASCADE'),
            useexisting = True,
            mysql_engine='INNODB'
        ))


    def debug(self, debug = True):
        self.db.debug = debug


    def set_table_prefix(self, prefix):
        self._table_prefix = prefix
        self.__update_table_names()


    def get_table_prefix(self):
        return self._table_prefix


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
        handle  = self._acl_section_handle
        success = self._acldb.delete_resource_section_from_handle(handle)
        if success:
            self._acl_section = None
        return success


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
            dependency_id_list.append(row[table.c.dependency_id])
        return dependency_id_list


    def __get_dependency_id_list(self, extension):
        assert extension is not None
        return self.__get_dependency_id_list_from_id(extension.get_id())


    def __get_dependency_descriptor_list_from_id(self, extension_id):
        assert extension_id >= 0
        table  = self._table_map['extension_dependency']
        query  = select([table.c.dependency_handle,
                         table.c.dependency_operator,
                         table.c.dependency_version],
                        table.c.extension_id == extension_id,
                        from_obj = [table])
        result = query.execute()
        assert result is not None

        dependency_list = []
        for row in result:
            handle   = row[table.c.dependency_handle]
            operator = row[table.c.dependency_operator]
            version  = row[table.c.dependency_version]
            dependency_list.append(handle + operator + version)
        return dependency_list


    def __get_dependency_descriptor_list(self, extension):
        assert extension is not None
        return self.__get_dependency_descriptor_list_from_id(extension.get_id())


    def __load_dependency_descriptor_list(self, extension):
        assert extension is not None
        list = self.__get_dependency_descriptor_list(extension)
        for dependency in list:
            extension.add_dependency(dependency)
        return True

    
    def __lookup_section(self):
        s_handle = self._acl_section_handle
        section  = self._acldb.get_resource_section_from_handle(s_handle)
        if not section:
            section = ResourceSection(s_handle)
            self._acldb.add_resource_section(section)
        self._acl_section = section
        


    def check_dependencies(self, extension):
        """
        Checks whether all required dependencies are registered.

        Returns True if all dependencies needed to register the given
        extension are registered, False otherwise.

        @type  extension: ExtensionInfo
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

        Inserts the given ExtensionInfo into the database.
        The method takes no action if the extension is already registered.

        @type  extension: ExtensionInfo
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

        # Make sure that a resource section already exists.
        if not self._acl_section:
            self.__lookup_section()

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
            table  = self._table_map['extension_dependency']
            query  = table.insert()
            result = query.execute(extension_id        = extension.get_id(),
                                   dependency_handle   = dependency_handle,
                                   dependency_operator = dependency_operator,
                                   dependency_version  = dependency_version)
            assert result is not None

            # And link the extension with the best matching dependency.
            best = self.get_extension_from_descriptor(descriptor)

            # Retrieve a list of all dependencies of that dependency.
            best_id = best.get_id()
            list    = self.__get_dependency_id_list_from_id(best_id)
            list.append(best_id)

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
        Removes the given ExtensionInfo from the database. Warning: Also
        removes any extension that requires the given ExtensionInfo.

        @type  id: int
        @param id: The id of the extension to remove.
        @rtype:  Boolean
        @return: False if the extension did not exist, True otherwise.
        """
        assert id >= 0
        dependency_list = self.__get_dependency_id_list_from_id(id)
        self._acldb.delete_resource_from_id(id)
        # Unregister all extensions that require this extension.
        for dependency_id in dependency_list:
            self._acldb.delete_resource_from_id(id)
        return True


    def unregister_extension_from_handle(self, handle, version):
        """
        Removes the given ExtensionInfo from the database.

        @type  handle: string
        @param handle: The handle of the extension to remove.
        @rtype:  Boolean
        @return: False if the extension did not exist, True otherwise.
        """
        assert handle is not None
        extension = self.get_extension_from_handle(handle, version)
        return self.unregister_extension_from_id(extension.get_id())


    def unregister_extension(self, extension):
        """
        Removes the given ExtensionInfo from the database.

        @type  extension: ExtensionInfo
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
        @rtype:  ExtensionInfo
        @return: The extension on success, None if it does not exist.
        """
        assert id >= 0
        extension = self._acldb.get_resource_from_id(id, 'ExtensionInfo')
        if extension is None:
            return None
        handle  = extension.get_handle()
        version = extension.get_version()
        extension.set_handle(handle[0:len(version) * -1])
        self.__load_dependency_descriptor_list(extension)
        return extension


    def get_extension_from_handle(self, handle, version):
        """
        Returns the extension with the given handle from the database.

        @type  handle:  string
        @param handle:  The handle of the wanted extension.
        @type  version: string
        @param version: The version number of the wanted extension.
        @rtype:  ExtensionInfo
        @return: The ExtensionInfo on success, None if none was found.
        """
        assert handle  is not None
        assert version is not None
        version_handle = make_handle_from_string(handle + version)
        section_handle = self._acl_section_handle
        extension      = self._acldb.get_resource_from_handle(version_handle,
                                                              section_handle,
                                                              'ExtensionInfo')
        if extension is None:
            return None
        extension.set_handle(handle)
        self.__load_dependency_descriptor_list(extension)
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
        @rtype:  ExtensionInfo
        @return: The ExtensionInfo on success, None if none was found.
        """
        assert descriptor is not None
        #print "Descriptor:", descriptor
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
        best_version = None
        for cur_version in version_list:
            if version_is_greater(version, cur_version.get_version()):
                continue
            if best_version is None:
                best_version = cur_version
                continue
            if version_is_greater(cur_version.get_version(),
                                  best_version.get_version()):
                best_version = cur_version
        if best_version is None:
            return None
        return best_version


    def get_version_list_from_handle(self, handle):
        """
        Returns a list of all registered versions that have the given
        handle.

        @type  handle: string
        @param handle: The handle of the wanted extension versions.
        @rtype:  list[ExtensionInfo]
        @return: A list containing all versions of the requested extension.
        """
        assert handle is not None
        # Make sure that a resource section already exists.
        if not self._acl_section:
            self.__lookup_section()

        section  = self._acl_section.get_handle()
        parent   = self._acldb.get_resource_from_handle(handle, section)
        if parent is None: return []
        children = self._acldb.get_resource_children(parent, 'ExtensionInfo')
        for child in children:
            child.set_handle(handle)
        return children


    def link_extension_id_to_callback(self, extension_id, uri):
        """
        Associates the given extension with the given callback.

        @type  extension_id: int
        @param extension_id: The id of the extension to be associated.
        @type  uri: Callback
        @param uri: The callback to be associated.
        @rtype:  int
        @return: The id of the callback, or <0 if an error occured.
        """
        assert extension_id >= 0
        assert uri is not None
        
        table  = self._table_map['extension_callback']
        query  = table.insert()
        result = query.execute(extension_id  = extension_id, event_uri = uri)
          #                     name          = callback.get_name(),
          #                     event_uri     = callback.get_event_uri())
        assert result is not None
        return result.last_inserted_ids()[0]


    def link_extension_to_callback(self, extension, uri):
        """
        Convenience wrapper around link_extension_id_to_callback().

        @type  extension: ExtensionInfo
        @param extension: The extension to be associated.
        @type  uri: Callback
        @param uri: The callback to be associated.
        @rtype:  int
        @return: The id of the callback, or <0 if an error occured.
        """
        return self.link_extension_id_to_callback(extension.get_id(), uri)


    def get_extension_id_list_from_callback(self, uri):
        """
        Returns a list of all extensions that are associated with the given
        uri.

        @type  uri: Callback
        @param uri: The callback to look for.
        @rtype:  list[int]
        @return: A list containing all associated extension ids, None on error.
        """
        assert uri is not None
        
        table  = self._table_map['extension_callback']
        #FIXME: Handle regexp callbacks.
        query  = select([table.c.extension_id],
                        table.c.event_uri == uri,
                        #and_(table.c.name      == callback.get_name(),
                        #     table.c.event_uri == callback.get_event_uri()),
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
    import Guard
    from ConfigParser import RawConfigParser

    class DBTest(unittest.TestCase):
        def set_table_prefix_test(self, db):
            assert db.clear_database()
            assert db.get_table_prefix() == ''
            db.set_table_prefix('test')
            assert db.get_table_prefix() == 'test'
            
        def check_dependencies_test(self, db):
            assert db.clear_database()
            extension = ExtensionInfo('Spiff')
            extension.set_version('0.2')
            db.register_extension(extension)
            
            extension = ExtensionInfo('Depends on Spiff')
            assert db.check_dependencies(extension)
            extension.add_dependency('spiff>=0.1')
            assert db.check_dependencies(extension)
            extension.add_dependency('spiff=0.2')
            assert db.check_dependencies(extension)
            extension.add_dependency('spuff>=0.1')
            assert not db.check_dependencies(extension)
            extension.add_dependency('spiff>=0.3')
            assert not db.check_dependencies(extension)

        def register_extension_test(self, db):
            assert db.clear_database()
            extension = ExtensionInfo('Spiff')
            extension.set_version('0.2')
            db.register_extension(extension)

        def unregister_extension_test(self, db):
            assert db.clear_database()
            extension = ExtensionInfo('Spiff')
            extension.set_version('0.1.2')
            db.register_extension(extension)
            assert db.unregister_extension_from_id(extension.get_id())

            extension = ExtensionInfo('Spiff')
            extension.set_version('0.1.2')
            db.register_extension(extension)
            assert db.unregister_extension_from_handle(extension.get_handle(),
                                                       extension.get_version())
            
            extension = ExtensionInfo('Spiff')
            extension.set_version('0.1.2')
            db.register_extension(extension)
            assert db.unregister_extension(extension)
            
        def get_extension_test(self, db):
            assert db.clear_database()
            extension = ExtensionInfo('Spiff')
            extension.set_version('0.1')
            db.register_extension(extension)

            extension = ExtensionInfo('Spiff')
            extension.set_version('0.2')
            extension.add_dependency('spiff=0.1')
            db.register_extension(extension)

            result = db.get_extension_from_id(extension.get_id())
            assert result.get_handle()  == extension.get_handle()
            assert result.get_version() == extension.get_version()
            assert len(result.get_dependency_list()) == 1
            assert result.get_dependency_list()[0]   == 'spiff=0.1'
            
            result = db.get_extension_from_handle('spiff', '0.2')
            assert result.get_id() == extension.get_id()

            result = db.get_extension_from_descriptor('spiff>=0.1')
            assert result.get_id()      == extension.get_id()
            assert result.get_handle()  == extension.get_handle()
            assert result.get_version() == extension.get_version()

            result = db.get_extension_from_descriptor('spiff=0.2')
            assert result.get_id()      == extension.get_id()
            assert result.get_handle()  == extension.get_handle()
            assert result.get_version() == extension.get_version()

            list = db.get_version_list_from_handle('spiff')
            assert len(list) == 2
            assert list[0].get_handle() == 'spiff'
            assert list[1].get_handle() == 'spiff'

        def dummy_callback(self, args):
            pass
            
        def callback_test(self, db):
            assert db.clear_database()
            extension = ExtensionInfo('Spiff')
            extension.set_version('0.1.2')
            db.register_extension(extension)

            #callback = Callback(self.dummy_callback, 'always')
            assert db.link_extension_id_to_callback(extension.get_id(),
                                                    'always')

            list = db.get_extension_id_list_from_callback('always')
            assert len(list) == 1
            

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
            acldb = Guard.DB(db)

            # Install.
            extdb = DB(acldb)
            assert extdb.uninstall()
            assert acldb.uninstall()
            assert acldb.install()
            assert extdb.install()

            # Test.
            self.set_table_prefix_test(extdb)
            self.register_extension_test(extdb)
            self.check_dependencies_test(extdb)
            self.unregister_extension_test(extdb)
            self.get_extension_test(extdb)
            self.callback_test(extdb)

            # Clean up.
            assert extdb.clear_database()
            assert extdb.uninstall()
            assert acldb.uninstall()


    testcase = DBTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
