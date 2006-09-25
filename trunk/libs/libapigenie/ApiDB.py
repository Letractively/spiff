import sys
sys.path.append('..')

from sqlalchemy import *

class ApiDB:
    def __init__(self, db):
        self.db            = db
        self._table_prefix = ''
        self._table_map    = {}
        self._table_list   = []
        self.__update_table_names()


    def __add_table(self, table):
        self._table_list.append(table)
        self._table_map[table.name] = table


    def __update_table_names(self):
        metadata = BoundMetaData(self.db)
        self.__add_table(Table('file', metadata,
            Column('id',     Integer,     primary_key = True),
            Column('handle', String(230), unique = True),
            Column('name',   String(230), unique = True),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table('action', metadata,
            Column('id',             Integer,     primary_key = True),
            Column('section_handle', String(230), index = True),
            Column('handle',         String(230), unique = True),
            Column('name',           String(230), unique = True),
            ForeignKeyConstraint(['section_handle'],
                                 ['action_section.handle'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))


    def debug(self, debug = True):
        self.db.debug = debug


    def set_table_prefix(self, prefix):
        self._table_prefix = prefix


