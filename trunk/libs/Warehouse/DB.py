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
from functions import random_path
from Item      import Item
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from sqlalchemy import *

class DB:
    attrib_type_int, attrib_type_bool, attrib_type_string = range(3)

    def __init__(self, db):
        """
        Instantiates a new DB.
        
        @type  db: object
        @param db: An sqlalchemy database connection.
        @rtype:  DB
        @return: The new instance.
        """
        self.db            = db
        self.db_metadata   = BoundMetaData(self.db)
        self._table_prefix = 'warehouse_'
        self._table_map    = {}
        self._table_list   = []
        self.__update_table_names()


    def __add_table(self, table):
        """
        Adds a new table to the internal table list.
        
        @type  table: Table
        @param table: An sqlalchemy table.
        """
        pfx = self._table_prefix
        self._table_list.append(table)
        self._table_map[table.name[len(pfx):]] = table


    def __update_table_names(self):
        """
        Adds all tables to the internal table list.
        """
        pfx = self._table_prefix
        self.__add_table(Table(pfx + 'revision', self.db_metadata,
            Column('id',              Integer,     primary_key = True),
            Column('alias',           String(230), index = True),
            Column('revision_number', Integer,     index = True),
            Column('mime_type',       String(50)),
            Column('filename',        String(250)),
            Column('added',           DateTime),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'metadata', self.db_metadata,
            Column('id',              Integer,     primary_key = True),
            Column('revision_id',     Integer,     index = True),
            Column('name',            String(50)),
            Column('type',            Integer),
            Column('attr_string',     String(200)),
            Column('attr_int',        Integer),
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
        delete = self._table_map['revision'].delete()
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


    def __get_revision_from_row(self, row):
        """
        Given a database row (=a list of columns) from the result of an SQL
        query, this function copies the columns into the appropriate
        attributes of an Item object.

        @type  row: list
        @param row: A database row.
        @rtype:  Item
        @return: A new Item instance with the attributes from the row.
        """
        if not row: return None
        tbl_r = self._table_map['revision']
        item  = Item(row[tbl_r.c.alias])
        pathname = os.path.join(self.__directory_base, row[tbl_r.c.filename])
        item.set_id(row[tbl_r.c.id])
        item.set_revision(row[tbl_r.c.revision_number])
        item.set_mime_type(row[tbl_r.c.mime_type])
        item.set_filename(pathname)
        return item


    def __get_revision_from_query(self, query, always_list = False):
        """
        May return a revision list, a single revision, or None.
        If always_list is True, a list is returned even if only a single
        result was produced.
        Returns None on failure.
        
        @type  query: select
        @param query: An sqlalchemy query.
        @rtype:  Item|list[Item]
        @return: A new Item instance, list of Item instances, or None.
        """
        assert query is not None
        result = query.execute()
        assert result is not None
        row = result.fetchone()
        if not row and always_list:
            return []
        elif not row:
            return None

        tbl_r         = self._table_map['revision']
        tbl_m         = self._table_map['metadata']
        last_id       = None
        revision_list = []
        while row is not None:
            last_id  = row[tbl_r.c.id]
            revision = self.__get_revision_from_row(row)
            revision_list.append(revision)
            if not revision: break

            # Append all attributes.
            while 1:
                # Determine attribute type.
                if row[tbl_m.c.type] == self.attrib_type_int:
                    value = int(row[tbl_m.c.attr_int])
                elif row[tbl_m.c.type] == self.attrib_type_bool:
                    value = bool(row[tbl_m.c.attr_int])
                elif row[tbl_m.c.type] == self.attrib_type_string:
                    value = row[tbl_m.c.attr_string]

                # Append attribute.
                if row[tbl_m.c.type] is not None:
                    revision.set_attribute(row[tbl_m.c.name], value)
                row = result.fetchone()

                if not row: break
                if last_id != row[tbl_r.c.id]:
                    break

        if always_list:
            return revision_list
        if len(revision_list) == 1:
            return revision
        return revision_list


    def __has_attribute(self, revision_id, name):
        """
        Returns True if the given attribute exists in the database, False
        otherwise.

        @type  revision_id: integer
        @param revision_id: The id of the revision that has the attribute.
        @type  name: string
        @param name: The name of the attribute.
        @rtype:  boolean
        @return: True if the attribute exists, False otherwise.
        """
        assert revision_id >= 0
        assert name is not None
        table  = self._table_map['metadata']
        select = table.select(and_(table.c.revision_id == revision_id,
                                   table.c.name        == name))
        result = select.execute()
        assert result is not None
        row = result.fetchone()
        if row is not None: return True
        return False


    def __add_attribute(self, revision_id, name, value):
        """
        Inserts the given attribute into the database, or updates it if it
        already exists.
        
        @type  revision_id: integer
        @param revision_id: The id of the revision that has the attribute.
        @type  name: string
        @param name: The name of the attribute.
        @type  name: boolean|integer|string
        @param name: The value of the attribute.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert revision_id >= 0
        assert name is not None
        if self.__has_attribute(revision_id, name):
            return self.__update_attribute(revision_id, name, value)
        insert = self._table_map['metadata'].insert()
        if value is None:
            value = ''
        if type(value) == type(0):
            result = insert.execute(revision_id = revision_id,
                                    name        = name,
                                    type        = self.attrib_type_int,
                                    attr_int    = value)
        elif type(value) == type(True):
            result = insert.execute(revision_id = revision_id,
                                    name        = name,
                                    type        = self.attrib_type_bool,
                                    attr_int    = int(value))
            
        elif type(value) == type(''):
            result = insert.execute(revision_id = revision_id,
                                    name        = name,
                                    type        = self.attrib_type_string,
                                    attr_string = value)
        else:
            assert False # Unknown attribute type.
        assert result is not None
        return result.last_inserted_ids()[0]


    def __update_attribute(self, revision_id, name, value):
        """
        Updates the given attribute in the database.
        
        @type  revision_id: integer
        @param revision_id: The id of the revision that has the attribute.
        @type  name: string
        @param name: The name of the attribute.
        @type  name: boolean|integer|string
        @param name: The value of the attribute.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert revision_id >= 0
        assert name is not None
        table  = self._table_map['metadata']
        update = table.update(and_(table.c.revision_id == revision_id,
                                   table.c.name        == name))
        if value is None:
            value = ''
        if type(value) == type(0):
            result = update.execute(type        = self.attrib_type_int,
                                    name        = name,
                                    attr_int    = value)
        elif type(value) == type(True):
            result = update.execute(type        = self.attrib_type_bool,
                                    name        = name,
                                    attr_int    = int(value))
        elif type(value) == type(''):
            result = update.execute(type        = self.attrib_type_string,
                                    name        = name,
                                    attr_string = value)
        else:
            assert False # Unknown attribute type.
        assert result is not None
        return True


    def add_file(self, item):
        """
        Adds the given Item into the database as a new revision. Also
        updates the database id, revision number, and filename in the
        given object.

        @type  item: Item
        @param item: The item to be added.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert item is not None
        assert os.path.exists(item.get_source_filename())

        connection  = self.db.connect()
        transaction = connection.begin()

        # Find the latest version number in the database.
        latest_item = self.get_file_from_alias(item.get_alias())
        revision    = latest_item and latest_item.get_revision() + 1 or 1
        
        # Move or copy the file to the location in the data directory.
        subdir   = random_path(8)
        dirname  = os.path.join(self.__directory_base, subdir)
        filename = random_path(1)
        pathname = os.path.join(dirname, filename)
        while os.path.exists(pathname):
            filename = random_path(1)
            pathname = os.path.join(dirname, filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        if item.get_move_on_add():
            shutil.move(item.get_source_filename(), pathname)
        else:
            shutil.copy(item.get_source_filename(), pathname)
        item.set_filename(pathname)
        
        # Insert the new revision to the revision table.
        rel_pathname = os.path.join(subdir, filename)
        table  = self._table_map['revision']
        insert = table.insert()
        result = insert.execute(alias           = item.get_alias(),
                                revision_number = revision,
                                mime_type       = item.get_mime_type(),
                                filename        = rel_pathname)
        assert result is not None
        revision_id = result.last_inserted_ids()[0]

        # Save the attributes.
        attrib_dict = item.get_attribute_dict()
        for attrib_name in attrib_dict.keys():
            value = attrib_dict[attrib_name]
            self.__add_attribute(revision_id, attrib_name, value)

        transaction.commit()
        connection.close()
        item.set_id(revision_id)
        item.set_revision(revision)
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
        assert id > 0

        # Look the item up, because we need the path name.
        item = self.get_file_from_id(id)
        if item is None:
            return False
        
        # Delete the item from the revision table.
        table  = self._table_map['revision']
        delete = table.delete(table.c.id == id)
        result = delete.execute()
        assert result is not None

        if result.rowcount == 0:
            return False

        # Delete the file.
        try:
            os.remove(item.get_filename())
        except:
            pass

        return True


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


    def remove_files_from_alias(self, alias, revision = None):
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

        # Look the items up, because we need the path name.
        items = self.get_file_list_from_alias(alias, revision)
        if len(items) == 0:
            return False
        
        # Delete the items from the revision table.
        table  = self._table_map['revision']
        where  = table.c.alias == alias
        if revision is not None:
            where = and_(where, table.c.revision_number == revision)
        delete = table.delete(where)
        result = delete.execute()
        assert result is not None

        if result.rowcount == 0:
            return False

        # Delete the files.
        for item in items:
            try:
                os.remove(item.get_filename())
            except:
                pass
        return True


    def get_file_from_id(self, id):
        """
        Returns the revision of the item that has the given id.

        @type  id: integer
        @param id: The id of the revision of the file.
        @rtype:  Item
        @return: The item on success, None otherwise.
        """
        assert id >= 0
        tbl_r  = self._table_map['revision']
        tbl_m  = self._table_map['metadata']
        table  = outerjoin(tbl_r, tbl_m, tbl_r.c.id == tbl_m.c.revision_id)
        select = table.select(tbl_r.c.id == id, use_labels = True)
        return self.__get_revision_from_query(select)


    def get_file_from_alias(self, alias, revision = None):
        """
        Returns the requested revision of the item with the given alias.
        If no revision is given, the latest revision is returned.

        @type  alias: string
        @param alias: The alias of the file.
        @type  revision: integer
        @param revision: The revision number of the file.
        @rtype:  Item
        @return: The item on success, None otherwise.
        """
        assert alias is not None
        tbl_r  = self._table_map['revision']
        tbl_m  = self._table_map['metadata']
        table  = outerjoin(tbl_r, tbl_m, tbl_r.c.id == tbl_m.c.revision_id)
        where  = tbl_r.c.alias == alias
        if revision is not None:
            where = and_(where, tbl_r.c.revision_number == revision)
        select = table.select(where,
                              order_by   = [desc(tbl_r.c.revision_number)],
                              limit      = 1,
                              use_labels = True)
        return self.__get_revision_from_query(select)


    def get_file_list_from_alias(self,
                                 alias,
                                 descending = True,
                                 offset     = 0,
                                 limit      = 0):
        """
        Returns a list containing revisions of the file with the given alias.
        By default, the list is ordered descending by revision number.

        @type  alias: string
        @param alias: The alias of the file.
        @type  descending: boolean
        @param descending: When True, the list is ordered descending,
                           otherwise ascending.
        @type  offset: integer
        @param offset: When != 0, the first n items will be skipped.
        @type  limit: integer
        @param limit: When != 0, a maximum of n items is returned.
        @rtype:  list[Item]
        @return: A list of items on success, None otherwise.
        """
        assert alias is not None
        tbl_r    = self._table_map['revision']
        tbl_m    = self._table_map['metadata']
        table    = outerjoin(tbl_r, tbl_m, tbl_r.c.id == tbl_m.c.revision_id)
        if descending:
            order_by = [desc(tbl_r.c.revision_number)]
        else:
            order_by = [tbl_r.c.revision_number]
        select = table.select(tbl_r.c.alias == alias,
                              order_by   = order_by,
                              offset     = offset,
                              limit      = limit,
                              use_labels = True)
        return self.__get_revision_from_query(select, True)


if __name__ == '__main__':
    import unittest
    import MySQLdb
    from ConfigParser import RawConfigParser

    class DBTest(unittest.TestCase):
        def test_with_db(self, db):
            assert db is not None
            db = DB(db)
            db.set_directory('data')
            assert db.uninstall()
            assert db.install()

            # Add a revision of a file into the database.
            item = Item("my/alias")
            item.set_source_filename("test.py")
            assert db.add_file(item)
            assert item.get_revision() == 1

            # Add another revision of the file into the database.
            item.set_source_filename("test2.py")
            assert db.add_file(item)
            assert item.get_revision() == 2

            # Add a new revision, but this time user a string instead of a file.
            item.set_content("this is the new version of test.txt")
            assert db.add_file(item)
            assert item.get_revision() == 3

            # Retrieve the latest revision.
            item = db.get_file_from_alias("my/alias")
            assert item.get_revision() == 3
            #print "Latest revision is", item.get_revision()

            # Retrieve all revisions.
            items = db.get_file_list_from_alias("my/alias")
            #print "All revisions:", [item.get_revision() for item in items]
            assert len(items) == 3
            assert items[0].get_revision() == 3
            assert items[1].get_revision() == 2
            assert items[2].get_revision() == 1

            # Retrieve revision 2.
            item = db.get_file_from_alias("my/alias", 2)
            assert item.get_revision() == 2

            # Delete revision 2.
            assert db.remove_file(item)

            # Make sure that it is gone.
            items = db.get_file_list_from_alias("my/alias")
            assert len(items) == 2
            assert items[0].get_revision() == 3
            assert items[1].get_revision() == 1

            # Delete the remaining items.
            assert db.remove_files_from_alias("my/alias")

            # Make sure that they are gone.
            items = db.get_file_list_from_alias("my/alias")
            assert len(items) == 0

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
