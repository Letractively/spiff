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

class DB:
    def __init__(self, db):
        self.db            = db
        self.db_metadata   = BoundMetaData(self.db)
        self._table_prefix = 'warehouse_'
        self._table_map    = {}
        self._table_list   = []
        self.__update_table_names()


    def __add_table(self, table):
        self._table_list.append(table)
        self._table_map[table.name] = table


    def __update_table_names(self):
        pfx = self._table_prefix
        self.__add_table(Table(pfx + 'data', self.db_metadata,
            Column('id',        Integer,     primary_key = True),
            Column('handle',    String(230), index = True),
            Column('version',   Integer,     index = True),
            Column('mime_type', String(50)),
            Column('filename',  String(250)),
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
        delete = self._table_map['data'].delete()
        result = delete.execute()
        assert result is not None
        return True


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
