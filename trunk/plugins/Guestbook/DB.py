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
from Guestbook  import Guestbook
from Posting    import Posting
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
        self._table_prefix    = 'guestbook_'
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
        self.__add_table(Table(pfx + 'guestbook', self.db_metadata,
            Column('id',              Integer,     primary_key = True),
            Column('title',           String(50)),
            Column('descr',           String(250)),
            Column('added',           DateTime,    default = func.now()),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'posting', self.db_metadata,
            Column('id',              Integer,     primary_key = True),
            Column('guestbook_id',    Integer,     index = True),
            Column('title',           String(50)),
            Column('descr',           String(250)),
            Column('added',           DateTime,    default = func.now()),
            ForeignKeyConstraint(['guestbook_id'],
                                 [pfx + 'guestbook.id'],
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


    def __get_guestbook_from_row(self, row):
        """
        Given a database row (=a list of columns) from the result of an SQL
        query, this function copies the columns into the appropriate
        attributes of a Guestbook object.

        @type  row: list
        @param row: A database row.
        @rtype:  Guestbook
        @return: A new Guestbook instance with the attributes from the row.
        """
        if not row: return None
        table = self._table_map['guestbook']
        guestbook = Guestbook(row[table.c.title], row[table.c.descr])
        guestbook.set_id(row[table.c.id])
        guestbook.set_datetime(row[table.c.added])
        return guestbook


    def __get_guestbook_from_query(self, query, always_list = False):
        """
        May return a list of Guestbook objects, a single guestbook, or None.
        If always_list is True, a list is returned even if only a single
        result was produced.
        Returns None on failure.
        
        @type  query: select
        @param query: An sqlalchemy query.
        @rtype:  Guestbook|list[Guestbook]
        @return: A new Guestbook instance, list of Guestbook instances, or None.
        """
        assert query is not None
        result = query.execute()
        assert result is not None
        row = result.fetchone()
        if not row and always_list:
            return []
        elif not row:
            return None

        guestbooks = []
        while row is not None:
            guestbook = self.__get_guestbook_from_row(row)
            guestbooks.append(guestbook)
            row = result.fetchone()

        if always_list:
            return guestbooks
        if len(guestbooks) == 1:
            return guestbook
        return guestbooks


    def __get_posting_from_row(self, row):
        """
        Given a database row (=a list of columns) from the result of an SQL
        query, this function copies the columns into the appropriate
        attributes of a Posting object.

        @type  row: list
        @param row: A database row.
        @rtype:  Posting
        @return: A new Posting instance with the attributes from the row.
        """
        if not row: return None
        table   = self._table_map['posting']
        posting = Posting(row[table.c.title], row[table.c.descr])
        posting.set_id(row[table.c.id])
        posting.set_datetime(row[table.c.added])
        return posting


    def __get_posting_from_query(self, query, always_list = False):
        """
        May return a list of postings, a single posting, or None.
        If always_list is True, a list is returned even if only a single
        result was produced.
        Returns None on failure.
        
        @type  query: select
        @param query: An sqlalchemy query.
        @rtype:  Posting|list[Posting]
        @return: A new Posting instance, list of Posting instances, or None.
        """
        assert query is not None
        result = query.execute()
        assert result is not None
        row = result.fetchone()
        if not row and always_list:
            return []
        elif not row:
            return None

        posting_list = []
        while row is not None:
            posting = self.__get_posting_from_row(row)
            posting_list.append(posting)
            row = result.fetchone()

        if always_list:
            return posting_list
        if len(posting_list) == 1:
            return posting
        return posting_list


    def add_guestbook(self, guestbook):
        """
        Adds the given Guestbook into the database as a new revision. Also
        updates the database id in the given object.
        Behaves like update_guestbook() if the guestbook is already in the
        database.

        @type  guestbook: Guestbook
        @param guestbook: The guestbook to be added.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert guestbook is not None

        # Check if the guestbook is already in the database.
        if guestbook.get_id() >= 0:
            return self.update_guestbook(guestbook)
        
        # Insert the new revision to the revision table.
        insert = self._table_map['guestbook'].insert()
        result = insert.execute(title = guestbook.get_title(),
                                descr = guestbook.get_description())
        assert result is not None
        guestbook_id = result.last_inserted_ids()[0]
        guestbook.set_id(guestbook_id)
        return True


    def remove_guestbook_from_id(self, id):
        """
        Removes the guestbook with the given id from the database.

        @type  id: integer
        @param id: The id of the guestbook in the database.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert id > 0

        # Delete the guestbook.
        table  = self._table_map['guestbook']
        delete = table.delete(table.c.id == id)
        result = delete.execute()
        assert result is not None

        if result.rowcount == 0:
            return False

        return True


    def remove_guestbook(self, guestbook):
        """
        Convenience wrapper around remove_guestbook_from_id().
        Removes the given guestbook from the database.

        @type  guestbook: Guestbook
        @param guestbook: The Guestbook to be removed from the database.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert guestbook is not None
        assert guestbook.get_id() >= 0
        return self.remove_guestbook_from_id(guestbook.get_id())


    def get_guestbook_from_id(self, guestbook_id):
        """
        Returns the guestbook with the given id.

        @type  guestbook_id: integer
        @param guestbook_id: The id of the guestbook.
        @rtype:  Guestbook
        @return: The guestbook on success, None otherwise.
        """
        assert guestbook_id >= 0
        table  = self._table_map['guestbook']
        select = table.select(table.c.id == guestbook_id)
        return self.__get_guestbook_from_query(select)


    def add_posting(self, guestbook_id, posting):
        """
        Adds the given Posting into the database. Also updates the database id
        in the given object.
        Behaves like update_posting() if the posting is already in the database.

        @type  posting: Posting
        @param posting: The posting to be added.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert guestbook_id is not None
        assert posting    is not None

        # Check if the posting is already in the database.
        if posting.get_id() >= 0:
            return self.update_posting(posting)
        
        # Insert the new revision to the revision table.
        insert = self._table_map['posting'].insert()
        result = insert.execute(guestbook_id = guestbook_id,
                                title        = posting.get_title(),
                                descr        = posting.get_description())
        assert result is not None
        posting_id = result.last_inserted_ids()[0]
        posting.set_id(posting_id)
        return True


    def remove_posting_from_id(self, id):
        """
        Removes the posting with the given id from the database.

        @type  id: integer
        @param id: The id of the posting in the database.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert id > 0

        # Delete the posting.
        table  = self._table_map['posting']
        delete = table.delete(table.c.id == id)
        result = delete.execute()
        assert result is not None

        if result.rowcount == 0:
            return False

        return True


    def remove_posting(self, posting):
        """
        Convenience wrapper around remove_posting_from_id().
        Removes the given posting from the database.

        @type  posting: Posting
        @param posting: The Posting to be removed from the database.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert posting is not None
        assert posting.get_id() >= 0
        return self.remove_posting_from_id(posting.get_id())


    def get_posting_from_id(self, id):
        """
        Returns the posting that has the given id.

        @type  id: integer
        @param id: The id of the posting.
        @rtype:  Posting
        @return: The posting on success, None otherwise.
        """
        assert id >= 0
        table  = self._table_map['posting']
        select = table.select(table.c.id == id)
        return self.__get_posting_from_query(select)


    def get_postings_from_guestbook_id(self, guestbook_id, offset = 0, limit = 0):
        """
        Returns the list of postings from the guestbook with the given id.

        @type  guestbook_id: integer
        @param guestbook_id: The id of the guestbook.
        @rtype:  list[Posting]
        @return: The postings on success, None otherwise.
        """
        assert id >= 0
        table  = self._table_map['posting']
        select = table.select(table.c.guestbook_id == id)
        return self.__get_posting_from_query(select, True)


    def get_postings(self, guestbook, offset = 0, limit = 0):
        """
        Returns the list of postings from the given guestbook.

        @type  guestbook: Guestbook
        @param guestbook: The guestbook.
        @rtype:  list[Posting]
        @return: The postings on success, None otherwise.
        """
        assert guestbook is not None
        assert guestbook.get_id() > 0
        return self.get_postings_from_guestbook_id(guestbook.get_id(),
                                                   offset,
                                                   limit)


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

            # Create a guestbook.
            guestbook = Guestbook("my guestbook", "testdescription for the gb")
            assert db.add_guestbook(guestbook)
            assert posting.get_id() > 0

            # Add a posting into the guestbook.
            posting = Posting("my posting", "testdescr for my posting")
            assert db.add_posting(guestbook.get_id(), posting)
            assert posting.get_id() > 0

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
