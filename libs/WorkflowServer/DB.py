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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../Workflow'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import Workflow.Storage
import sqlalchemy.orm as orm
from sqlalchemy       import *
from WorkflowInfo     import WorkflowInfo
from JobInfo          import JobInfo
from TaskInfo         import TaskInfo

class DB:
    attrib_type_int, attrib_type_bool, attrib_type_string = range(3)

    def __init__(self, db):
        """
        Instantiates a new DBReader.
        
        @type  db: object
        @param db: An sqlalchemy database connection.
        @rtype:  DB
        @return: The new instance.
        """
        self.db            = db
        self.db_metadata   = BoundMetaData(self.db)
        # sqlalchemy 0.4
        #self.db_metadata   = MetaData(self.db)
        #self.session_maker = orm.sessionmaker(bind          = self.db,
        #                                      autoflush     = True,
        #                                      transactional = True)
        #self.session       = self.session_maker()
        self.session       = create_session()
        self.xml_parser    = None
        self._table_prefix = 'workflow_'
        self._table_list   = []
        self._table_map    = {}
        self._initialized  = False
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

        # Workflow table.
        table = Table(pfx + 'workflow',
                      self.db_metadata,
                      Column('id',     Integer,      primary_key = True),
                      Column('handle', String(200),  unique      = True),
                      Column('name',   String(50)),
                      Column('xml',    String(230)),
                      mysql_engine = 'INNODB')
        if not self._initialized:
            mapper = orm.mapper(WorkflowInfo, table)
        self.__add_table(table)

        # Job table.
        table = Table(pfx + 'job',
                      self.db_metadata,
                      Column('id',          Integer,      primary_key = True),
                      Column('workflow_id', Integer,      index       = True),
                      Column('status',      String(50)),
                      Column('last_change', DateTime()),
                      Column('instance',    PickleType()),
                      ForeignKeyConstraint(['workflow_id'],
                                           [pfx + 'workflow.id'],
                                           ondelete = 'CASCADE'),
                      mysql_engine = 'INNODB')
        if not self._initialized:
            mapper = orm.mapper(JobInfo,
                                table,
                                properties = {
                                    'instance': deferred(table.c.instance)
                                })
        self.__add_table(table)

        # Task table.
        table = Table(pfx + 'task',
                      self.db_metadata,
                      Column('id',          Integer,      primary_key = True),
                      Column('job_id',      Integer,      index       = True),
                      Column('name',        String(230)),
                      Column('status',      String(50)),
                      Column('last_change', DateTime()),
                      ForeignKeyConstraint(['job_id'],
                                           [pfx + 'job.id'],
                                           ondelete = 'CASCADE'),
                      mysql_engine = 'INNODB')
        if not self._initialized:
            mapper = orm.mapper(TaskInfo, table)
        self.__add_table(table)

        self._initialized = True


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
        self.db_metadata.drop_all()
        return True
        #for table in self._table_list[::-1]:
        #    table.drop(checkfirst = True)
        #return True


    def clear_database(self):
        """
        Drops the content of any database table used by this library.
        Use with care.

        Wipes out everything, including sections, actions, resources and acls.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        delete = self._table_map['workflow'].delete()
        result = delete.execute()
        assert result is not None

        delete = self._table_map['job'].delete()
        result = delete.execute()
        assert result is not None

        delete = self._table_map['task'].delete()
        result = delete.execute()
        assert result is not None
        return True


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
        self._table_prefix = prefix
        self.__update_table_names()


    def get_table_prefix(self):
        """
        Returns the current database table prefix.
        
        @rtype:  string
        @return: The current prefix.
        """
        return self._table_prefix


    def __get_xml_parser(self):
        if self.xml_parser is None:
            self.xml_parser = Workflow.Storage.XmlParser()
        return self.xml_parser


    def get_workflow(self, **filter):
        return self.session.query(WorkflowInfo).select_by(**filter)


    def get_job(self, **filter):
        return self.session.query(JobInfo).select_by(**filter)


    def get_task(self, **filter):
        return self.session.query(TaskInfo).select_by(**filter)


    def delete(self, object):
        if object is None:
            raise Exception('object argument is None')
        self.session.delete(object)
        self.session.flush()


    def save(self, object):
        if object is None:
            raise Exception('object argument is None')
        result = self.session.save(object)
        #self.session.commit() #sqlalchemy0.4
        self.session.flush()
        return result