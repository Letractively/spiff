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
from Wishlist   import Wishlist
from Wish       import Wish
from sqlalchemy import *

class DB:
    def __init__(self, db):
        """
        Instantiates a new DB.
        
        @type  db: object
        @param db: An sqlalchemy database connection.
        @rtype:  DB
        @return: The new instance.
        """
        self.db               = db
        self.db_metadata      = BoundMetaData(self.db)
        self._table_prefix    = 'wishlist_'
        self._table_map       = {}
        self._table_list      = []
        self.__directory_base = ''
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
        self._table_list = []
        self.__add_table(Table(pfx + 'list', self.db_metadata,
            Column('id',              Integer,     primary_key = True),
            Column('title',           String(50)),
            Column('descr',           String(250)),
            Column('added',           DateTime,    default = func.now()),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'wish', self.db_metadata,
            Column('id',              Integer,     primary_key = True),
            Column('list_id',         Integer,     index = True),
            Column('title',           String(50)),
            Column('descr',           String(250)),
            Column('added',           DateTime,    default = func.now()),
            ForeignKeyConstraint(['list_id'],
                                 [pfx + 'list.id'],
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


    def __get_wishlist_from_row(self, row):
        """
        Given a database row (=a list of columns) from the result of an SQL
        query, this function copies the columns into the appropriate
        attributes of a Wishlist object.

        @type  row: list
        @param row: A database row.
        @rtype:  Wishlist
        @return: A new Wishlist instance with the attributes from the row.
        """
        if not row: return None
        table = self._table_map['list']
        wishlist  = Wishlist(row[table.c.title], row[table.c.descr])
        wishlist.set_id(row[table.c.id])
        wishlist.set_datetime(row[table.c.added])
        return wishlist


    def __get_wishlist_from_query(self, query, always_list = False):
        """
        May return a list of Wishlist objects, a single wishlist, or None.
        If always_list is True, a list is returned even if only a single
        result was produced.
        Returns None on failure.
        
        @type  query: select
        @param query: An sqlalchemy query.
        @rtype:  Wishlist|list[Wishlist]
        @return: A new Wishlist instance, list of Wishlist instances, or None.
        """
        assert query is not None
        result = query.execute()
        assert result is not None
        row = result.fetchone()
        if not row and always_list:
            return []
        elif not row:
            return None

        wishlists = []
        while row is not None:
            wishlist = self.__get_wishlist_from_row(row)
            wishlists.append(wishlists)
            row = result.fetchone()

        if always_list:
            return wishlists
        if len(wishlists) == 1:
            return wishlist
        return wishlists


    def __get_wish_from_row(self, row):
        """
        Given a database row (=a list of columns) from the result of an SQL
        query, this function copies the columns into the appropriate
        attributes of a Wish object.

        @type  row: list
        @param row: A database row.
        @rtype:  Wish
        @return: A new Wish instance with the attributes from the row.
        """
        if not row: return None
        table = self._table_map['wish']
        wish  = Wish(row[table.c.title], row[table.c.descr])
        wish.set_id(row[table.c.id])
        wish.set_datetime(row[table.c.added])
        return wish


    def __get_wish_from_query(self, query, always_list = False):
        """
        May return a list of wishes, a single wish, or None.
        If always_list is True, a list is returned even if only a single
        result was produced.
        Returns None on failure.
        
        @type  query: select
        @param query: An sqlalchemy query.
        @rtype:  Wish|list[Wish]
        @return: A new Wish instance, list of Wish instances, or None.
        """
        assert query is not None
        result = query.execute()
        assert result is not None
        row = result.fetchone()
        if not row and always_list:
            return []
        elif not row:
            return None

        wish_list = []
        while row is not None:
            wish = self.__get_wish_from_row(row)
            wish_list.append(wish)

        if always_list:
            return wish_list
        if len(wish_list) == 1:
            return wish
        return wish_list


    def add_wishlist(self, wishlist):
        """
        Adds the given Wishlist into the database as a new revision. Also
        updates the database id in the given object.
        Behaves like update_wishlist() if the wishlist is already in the
        database.

        @type  wishlist: Wishlist
        @param wishlist: The wishlist to be added.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert wishlist is not None

        # Check if the wishlist is already in the database.
        if wishlist.get_id() >= 0:
            return self.update_wishlist(wishlist)
        
        # Insert the new revision to the revision table.
        insert = self._table_map['list'].insert()
        result = insert.execute(list_id = list_id,
                                title   = wishlist.get_title(),
                                descr   = wishlist.get_description())
        assert result is not None
        wishlist_id = result.last_inserted_ids()[0]
        wishlist.set_id(wishlist_id)
        return True


    def remove_wishlist_from_id(self, id):
        """
        Removes the wishlist with the given id from the database.

        @type  id: integer
        @param id: The id of the wishlist in the database.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert id > 0

        # Delete the wishlist.
        table  = self._table_map['list']
        delete = table.delete(table.c.id == id)
        result = delete.execute()
        assert result is not None

        if result.rowcount == 0:
            return False

        return True


    def remove_wishlist(self, wishlist):
        """
        Convenience wrapper around remove_wishlist_from_id().
        Removes the given wishlist from the database.

        @type  wishlist: Wishlist
        @param wishlist: The Wishlist to be removed from the database.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert wishlist is not None
        assert wishlist.get_id() >= 0
        return self.remove_wishlist_from_id(wishlist.get_id())


    def get_wishlist_from_id(self, list_id):
        """
        Returns the wishlist with the given id.

        @type  list_id: integer
        @param list_id: The id of the wishlist.
        @rtype:  Wishlist
        @return: The wishlist on success, None otherwise.
        """
        assert id >= 0
        table  = self._table_map['list']
        select = table.select(table.c.id == id)
        return self.__get_wishlist_from_query(select)


    def add_wish(self, list_id, wish):
        """
        Adds the given Wish into the database. Also updates the database id
        in the given object.
        Behaves like update_wish() if the wish is already in the database.

        @type  wish: Wish
        @param wish: The wish to be added.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert list_id is not None
        assert wish    is not None

        # Check if the wish is already in the database.
        if wish.get_id() >= 0:
            return self.update_wish(wish)
        
        # Insert the new revision to the revision table.
        insert = self._table_map['wish'].insert()
        result = insert.execute(list_id = list_id,
                                title   = wish.get_title(),
                                descr   = wish.get_description())
        assert result is not None
        wish_id = result.last_inserted_ids()[0]
        wish.set_id(wish_id)
        return True


    def remove_wish_from_id(self, id):
        """
        Removes the wish with the given id from the database.

        @type  id: integer
        @param id: The id of the wish in the database.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert id > 0

        # Delete the wish.
        table  = self._table_map['wish']
        delete = table.delete(table.c.id == id)
        result = delete.execute()
        assert result is not None

        if result.rowcount == 0:
            return False

        return True


    def remove_wish(self, wish):
        """
        Convenience wrapper around remove_wish_from_id().
        Removes the given wish from the database.

        @type  wish: Wish
        @param wish: The Wish to be removed from the database.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert wish is not None
        assert wish.get_id() >= 0
        return self.remove_wish_from_id(wish.get_id())


    def get_wish_from_id(self, id):
        """
        Returns the wish that has the given id.

        @type  id: integer
        @param id: The id of the wish.
        @rtype:  Wish
        @return: The wish on success, None otherwise.
        """
        assert id >= 0
        table  = self._table_map['wish']
        select = table.select(table.c.id == id)
        return self.__get_wish_from_query(select)


    def get_wishes_from_list_id(self, list_id, offset = 0, limit = 0):
        """
        Returns the list of wishes from the list with the given id.

        @type  list_id: integer
        @param list_id: The id of the wishlist.
        @rtype:  list[Wish]
        @return: The wishes on success, None otherwise.
        """
        assert id >= 0
        tbl_l  = self._table_map['list']
        tbl_w  = self._table_map['wish']
        table  = tbl_l.outerjoin(tbl_w, tbl_l.c.id == tbl_w.c.list_id)
        select = table.select(tbl_l.c.id == id, use_labels = True)
        return self.__get_wish_from_query(select, True)


    def get_wishes(self, wishlist, offset = 0, limit = 0):
        """
        Returns the list of wishes from the given list.

        @type  wishlist: Wishlist
        @param wishlist: The wishlist.
        @rtype:  list[Wish]
        @return: The wishes on success, None otherwise.
        """
        assert wishlist is not None
        assert wishlist.get_id() > 0
        tbl_l  = self._table_map['list']
        tbl_w  = self._table_map['wish']
        table  = tbl_l.outerjoin(tbl_w, tbl_l.c.id == tbl_w.c.list_id)
        select = table.select(tbl_l.c.id == wishlist.get_id(),
                              use_labels = True)
        return self.__get_wish_from_query(select, True)


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

            # Create a wishlist.
            wishlist = Wishlist("my wishlist", "testdescription for the list")
            assert db.add_wishlist(wishlist)
            assert wish.get_id() > 0

            # Add a wish into the list.
            wish = Wish("my wish", "testdescr for my wish")
            assert db.add_wish(wishlist.get_id(), wish)
            assert wish.get_id() > 0

            #FIXME: Add missing tests.

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
