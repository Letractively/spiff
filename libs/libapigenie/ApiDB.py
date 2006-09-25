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
        pfx = self._table_prefix
        self.__add_table(Table(pfx + 'api_documentation', metadata,
            Column('id',            Integer, primary_key = True),
            Column('documentation', Text),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'fs_dir', metadata,
            Column('id',   Integer, primary_key = True),
            Column('name', Integer),
            Column('api_documentation_id', Integer),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'fs_file', metadata,
            Column('id',                   Integer, primary_key = True),
            Column('name',                 Integer),
            Column('api_documentation_id', Integer),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'source_chunk', metadata,
            Column('id',                   Integer, primary_key = True),
            Column('name',                 String(230)),
            Column('data',                 String(230)),
            Column('api_documentation_id', Integer),
            ForeignKeyConstraint(['api_documentation_id'],
                                 ['api_documentation.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'source_tree', metadata,
            Column('id',              Integer,     primary_key = True),
            Column('source_chunk_id', Integer),
            Column('path',            Binary(255), unique = True),
            Column('depth',           Integer),
            Column('n_children',      Integer),
            ForeignKeyConstraint(['source_chunk_id'],
                                 ['source_chunk.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'source_tree_ancestor_map', metadata,
            Column('chunk_id',    Integer, unique = True),
            Column('ancestor_id', Integer),
            ForeignKeyConstraint(['chunk_id'],
                                 ['source_tree.id'],
                                 ondelete = 'CASCADE'),
            ForeignKeyConstraint(['ancestor_id'],
                                 ['source_tree.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'api_class', metadata,
            Column('id',              Integer, primary_key = True),
            Column('source_chunk_id', Integer),
            ForeignKeyConstraint(['source_chunk_id'],
                                 ['source_chunk.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'api_function', metadata,
            Column('id',              Integer, primary_key = True),
            Column('source_chunk_id', Integer),
            ForeignKeyConstraint(['source_chunk_id'],
                                 ['source_chunk.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'variable', metadata,
            Column('id',                   Integer, primary_key = True),
            Column('name',                 String(100)),
            Column('var_type',             String(100)),
            Column('api_documentation_id', Integer),
            ForeignKeyConstraint(['api_documentation_id'],
                                 ['api_documentation.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'api_function_argument_map', metadata,
            Column('api_function_id', Integer),
            Column('argument_id',     Integer),
            ForeignKeyConstraint(['api_function_id'],
                                 ['api_function.id'],
                                 ondelete = 'CASCADE'),
            ForeignKeyConstraint(['argument_id'],
                                 ['variable.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'api_function_return_map', metadata,
            Column('api_function_id', Integer),
            Column('return_id',       Integer),
            ForeignKeyConstraint(['api_function_id'],
                                 ['api_function.id'],
                                 ondelete = 'CASCADE'),
            ForeignKeyConstraint(['return_id'],
                                 ['variable.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))


    def debug(self, debug = True):
        self.db.debug = debug


    def set_table_prefix(self, prefix):
        self._table_prefix = prefix


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
        delete = self._table_map['source_chunk'].delete()
        result = delete.execute()
        assert result is not None
        return True


    def __add_documentation(self, doc):
        table  = self._table_map['api_documentation']
        insert = table.insert(doc = doc)
        result = insert.execute()
        assert result is not None
        return result.get_last_inserted_ids()[0]


    def add_directory(self, parent_id, directory):
        """
        Inserts the given directory object into the database.
        
        @type  parent_id: int
        @param parent_id: The id of the directory under which the new
                          directory is added.
        @type  directory: Directory
        @param directory: The directory that is added.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert directory is not None

        connection  = self.db.connect()
        transaction = connection.begin()

        #FIXME

        transaction.commit()
        directory.set_id(directory_id)
        return True


    def get_directory_from_id(self, id):
        """
        Returns the directory with the given id from the database.

        @type  id: int
        @param id: The id of the wanted directory.
        @rtype:  Directory
        @return: The Directory instance on success, None otherwise.
        """
        tbl_f  = self._table_map['fs_dir']
        tbl_d  = self._table_map['api_documentation']
        table  = join(tbl_f, tbl_d, tbl_d.c.id == tbl_f.c.api_documentation_id)
        select = table.select(table.c.id == id)
        result = select.execute()
        assert result is not None
        row = result.fetchone()
        if row is None: return None
        directory = Directory(row['name'])
        directory.set_id(id)
        directory.set_doc(row['doc'])
        return directory


    def remove_directory_from_id(self, id):
        """
        Removes the directory with the given id from the database,
        including all sub-directories and files.

        @type  id: int
        @param id: The id of the directory that is deleted.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        #FIXME
        return True


    def remove_directory(self, directory):
        """
        Removes the given directory from the database.

        @type  directory: Directory
        @param directory: The directory that is deleted.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        return self.remove_directory_from_id(directory.get_id())
        

    def add_file(self, parent_id, file):
        """
        Inserts the given file object into the database.
        
        @type  parent_id: int
        @param parent_id: The id of the directory under which the new
                          file is added.
        @type  file: File
        @param file: The file that is added.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert file is not None

        connection  = self.db.connect()
        transaction = connection.begin()

        #FIXME

        transaction.commit()
        file.set_id(file_id)
        return True


    def get_file_from_id(self, id):
        """
        Returns the file with the given id from the database.

        @type  id: int
        @param id: The id of the wanted file.
        @rtype:  File
        @return: The File instance on success, None otherwise.
        """
        tbl_f  = self._table_map['fs_file']
        tbl_d  = self._table_map['api_documentation']
        table  = join(tbl_f, tbl_d, tbl_d.c.id == tbl_f.c.api_documentation_id)
        select = table.select(table.c.id == id)
        result = select.execute()
        assert result is not None
        row = result.fetchone()
        if row is None: return None
        file = File(row['name'])
        file.set_id(id)
        file.set_doc(row['doc'])
        return file


    def remove_file_from_id(self, id):
        """
        Removes the file with the given id from the database.

        @type  id: int
        @param id: The id of the file that is deleted.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        #FIXME
        return True


    def remove_file(self, file):
        """
        Removes the given file from the database.

        @type  file: File
        @param file: The file that is deleted.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        return self.remove_file_from_id(file.get_id())
