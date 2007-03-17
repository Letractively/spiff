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
import os
import os.path
import shutil
from stat import *
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from sqlalchemy import *

class DB:
    def __init__(self, db):
        self.db            = db
        self.db_metadata   = BoundMetaData(self.db)
        self._table_prefix = 'warehouse_'
        self._table_map    = {}
        self._table_list   = []
        self.__update_table_names()


    def __add_table(self, table):
        pfx = self._table_prefix
        self._table_list.append(table)
        self._table_map[table.name[len(pfx):]] = table


    def __update_table_names(self):
        pfx = self._table_prefix
        self.__add_table(Table(pfx + 'data', self.db_metadata,
            Column('id',          Integer,     primary_key = True),
            Column('alias',       String(230), unique = True),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'revision', self.db_metadata,
            Column('id',          Integer,     primary_key = True),
            Column('data_id',     Integer,     index = True),
            Column('number',      Integer,     index = True),
            Column('mime_type',   String(50)),
            Column('filename',    String(250)),
            Column('changes',     String(250)),
            Column('added',       DateTime),
            ForeignKeyConstraint(['data_id'],
                                 [pfx + 'data.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'metadata', self.db_metadata,
            Column('id',          Integer,     primary_key = True),
            Column('revision_id', Integer,     index = True),
            Column('name',        String(50)),
            Column('type',        Integer),
            Column('attr_string', String(200)),
            Column('attr_int',    Integer),
            ForeignKeyConstraint(['revision_id'],
                                 [pfx + 'revision.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))


    def debug(self, debug = True):
        """
        Enable/disable debugging.

        @type  debug: Boolean
        @param debug: True to enable debugging.
        """
        self.db.debug = debug


    def set_table_prefix(self, prefix):
        """
        Define a table prefix. Default is 'warehouse_'.

        @type  prefix: string
        @param prefix: The new prefix.
        """
        assert prefix is not None
        self._table_prefix = prefix
        self.__update_table_names()


    def get_table_prefix(self):
        """
        Returns the current database table prefix.
        
        @rtype:  string
        @return: The current prefix.
        """
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
        delete = self._table_map['data'].delete()
        result = delete.execute()
        assert result is not None
        return True


    def set_directory(self, directory):
        """
        Defines base of the data directory.

        @type  directory: string
        @param directory: The name of the directory to be added.
        """
        mode = os.stat(directory)[ST_MODE]
        assert S_ISDIR(mode)     # Argument must be a directory.
        assert mode & S_IWRITE   # Reqire write permissions.
        self.__directory_base = directory


    def add_file(self, item):
        """
        Adds the given Item into the database as a new revision. Also
        updates the database id and revision number in the given object.

        @type  item: Item
        @param item: The item to be added.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert filename is not None
        assert os.path.exists(filename)
        assert metadata is not None
        if name is None:
            name = filename
        # Check whether the file already exists in the data table.
        #FIXME
        
        # Insert the new revision to the revision table.
        #FIXME

        # Append the metadata.
        #FIXME
        return True


    def remove_file_from_id(self, id):
        """
        Removes the version of the file with the given id from the
        database.

        @type  id: integer
        @param id: The name of the file in the database.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert id is not None
        #FIXME: Delete the item from the revision table.


    def remove_file(self, item):
        """
        Convenience wrapper around remove_file_from_id().
        Removes the given revision of the item from the database.

        @type  item: Item
        @param item: The Item to be removed from the database.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert item is not None
        assert item.get_id() >= 0
        return self.remove_file_from_id(item.get_id())


    def remove_files_from_alias(self, alias, version = None):
        """
        Removes the version of the file with the given alias from the
        database. If no version number is specified, all versions are
        removed.

        @type  alias: string
        @param alias: The name of the file in the database.
        @type  revision: integer
        @param revision: The revision number of the file in the database.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert alias is not None
        #FIXME


    def get_item_from_alias(self, alias):
        """
        Returns the latest revision of the item with the given alias.

        @type  alias: string
        @param alias: The alias of the file.
        @rtype:  Item
        @return: The item on success, None otherwise.
        """
        assert alias is not None
        #FIXME
        return None


    def get_item_list_from_alias(self, alias, offset = 0, limit = 0):
        """
        Returns a list containing revisions of the file with the given alias.
        The list is ordered by revision number (ascending).

        @type  alias: string
        @param alias: The alias of the file.
        @type  offset: integer
        @param offset: When != 0, the first n items will be skipped.
        @type  limit: integer
        @param limit: When != 0, a maximum of n items is returned.
        @rtype:  list[Item]
        @return: A list of items on success, None otherwise.
        """
        assert alias is not None
        #FIXME
        return None


if __name__ == '__main__':
    import unittest
    import MySQLdb
    from ConfigParser import RawConfigParser

    class DBTest(unittest.TestCase):
        def test_with_db(self, db):
            assert db is not None
            db = DB(db)
            assert db.uninstall()
            assert db.install()

            #FIXME: Do something.
            db.set_directory('data')

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
            auth = user + ':' + password
            dbn  = 'mysql://' + auth + '@' + host + '/' + db_name
            #print dbn
            db   = create_engine(dbn)
            self.test_with_db(db)

    testcase = DBTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
