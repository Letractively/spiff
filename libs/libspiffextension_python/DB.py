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
    def __init__(self, acldb, section_handle):
        self.db            = acldb.db
        self._acldb        = acldb
        self._table_prefix = ''
        self._table_map    = {}
        self._table_list   = []
        self._acl_section  = libspiffacl_python.ActionSection(section_handle)
        self.__update_table_names()


    def __add_table(self, table):
        self._table_list.append(table)
        self._table_map[table.name] = table


    def __update_table_names(self):
        metadata = BoundMetaData(self.db)
        pfx = self._table_prefix
        self.__add_table(Table(pfx + 'extension_dependency', metadata,
            Column('id',                  Integer,    primary_key = True),
            Column('extension_id',        Integer),
            Column('dependency_handle',   String(20), index = True),
            Column('dependency_operator', String(3),  index = True),
            Column('dependency_version',  String(20), index = True),
            #FIXME: Request the name of the destination table from self._acldb.
            ForeignKeyConstraint(['extension_id'],
                                 ['resource.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'extension_dependency_map', metadata,
            Column('extension_id',  Integer),
            Column('dependency_id', Integer),
            #FIXME: Request the name of the destination table from self._acldb.
            ForeignKeyConstraint(['extension_id'],
                                 ['resource.id'],
                                 ondelete = 'CASCADE'),
            #FIXME: Request the name of the destination table from self._acldb.
            ForeignKeyConstraint(['dependency_id'],
                                 ['resource.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'extension_callback', metadata,
            Column('id',           Integer,     primary_key = True),
            Column('extension_id', Integer),
            Column('name',         String(200)),
            Column('event_uri',    String(255), index = True),
            #FIXME: Request the name of the destination table from self._acldb.
            ForeignKeyConstraint(['extension_id'],
                                 ['resource.id'],
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
        return self.acldb.clear_section(self._acl_section)


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
        #FIXME


    def __get_dependency_id_list(self, extension):
        assert extension is not None
        return self.__get_dependency_id_list_from_id(extension.get_id())


    def __get_dependency_list_from_id(self, extension_id):
        assert extension_id >= 0
        #FIXME


    def __get_dependency_list(self, extension):
        assert extension is not None
        return self.__get_dependency_list_from_id(extension.get_id())


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
        #FIXME
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
        #FIXME
        return True


    def unregister_extension(self, extension):
        """
        Removes the given Extension from the database.

        @type  extension: Extension
        @param extension: The extension to remove.
        @rtype:  Boolean
        @return: False if the extension did not exist, True otherwise.
        """
        assert extension is not None
        #FIXME
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
        #FIXME
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
        assert handle is not None
        #FIXME
        return extension


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
        #FIXME
        return extension


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
        #FIXME
        return version_list


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
        return self._db.last_insert_id


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
    from ConfigParser import RawConfigParser

    class ExtensionDBTest(unittest.TestCase):
        def test_with_db(self, db):
            assert db is not None
            #FIXME
            #acldb = libspiffacl_python.DB(db)
            #extdb = DB(acldb)
            #assert db.uninstall()
            #assert db.install()

            # Clean up.
            #assert db.clear_database()
            #assert db.uninstall()


        def runTest(self):
            # Read config.
            cfg = RawConfigParser()
            cfg.read('unit_test.cfg')
            host     = cfg.get('database', 'host')
            db_name  = cfg.get('database', 'db_name')
            user     = cfg.get('database', 'user')
            password = cfg.get('database', 'password')

            # Connect to MySQL.
            auth = user + ':' + password
            dbn  = 'mysql://' + auth + '@' + host + '/' + db_name
            #print dbn
            db   = create_engine(dbn)
            self.test_with_db(db)

    testcase = ExtensionDBTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
