import sys
sys.path.append('..')
from DocumentModel import *
from functions     import *
from sqlalchemy    import *

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
        self.__add_table(Table(pfx + 'fs_tree', metadata,
            Column('id',              Integer,     primary_key = True),
            Column('path',            Binary(255), unique = True),
            Column('depth',           Integer),
            Column('n_children',      Integer),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'fs_tree_ancestor_map', metadata,
            Column('node_id',     Integer, unique = True),
            Column('ancestor_id', Integer),
            ForeignKeyConstraint(['node_id'],
                                 ['fs_tree.id'],
                                 ondelete = 'CASCADE'),
            ForeignKeyConstraint(['ancestor_id'],
                                 ['fs_tree.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'fs_dir', metadata,
            Column('id',            Integer, primary_key = True),
            Column('node_id',       Integer),
            Column('name',          String(100)),
            Column('documentation', TEXT),
            ForeignKeyConstraint(['node_id'],
                                 ['fs_tree.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'fs_file', metadata,
            Column('id',            Integer, primary_key = True),
            Column('node_id',       Integer),
            Column('name',          String(100)),
            Column('documentation', TEXT),
            ForeignKeyConstraint(['node_id'],
                                 ['fs_tree.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'source_chunk', metadata,
            Column('id',            Integer, primary_key = True),
            Column('node_id',       Integer),
            Column('name',          String(230)),
            Column('data',          String(230)),
            Column('documentation', TEXT),
            ForeignKeyConstraint(['node_id'],
                                 ['fs_tree.id'],
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
        self.__add_table(Table(pfx + 'argument', metadata,
            Column('id',              Integer, primary_key = True),
            Column('api_function_id', Integer),
            Column('name',            String(100)),
            Column('type',            String(100)),
            Column('documentation',   TEXT),
            ForeignKeyConstraint(['api_function_id'],
                                 ['api_function.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'return_value', metadata,
            Column('id',              Integer, primary_key = True),
            Column('api_function_id', Integer),
            Column('type',            String(100)),
            Column('documentation',   TEXT),
            ForeignKeyConstraint(['api_function_id'],
                                 ['api_function.id'],
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


    def __get_node_path_from_id(self, id):
        assert id is not None
        table  = self._table_map['fs_tree']
        query  = select([table.c.path],
                        table.c.id == id,
                        from_obj = [table])
        result = query.execute()
        assert result is not None
        row = result.fetchone()
        if not row: return None
        length = len(row['path'])
        path   = bin_path2hex_path(row['path'])
        return path


    def __node_add_n_children(self, node_id, n_children):
        assert node_id    >= 0
        assert n_children >= 0
        table  = self._table_map['fs_tree']
        update = table.update(table.c.id == id)
        result = update.execute(n_children = table.c.n_children + n_children)
        assert result is not None


    def __add_node(self, parent_id):
        connection  = self.db.connect()
        transaction = connection.begin()

        # Fetch parent path and increase the parent's child counter.
        if parent_id is None:
            parent_path = ''
        else:
            parent_path = self.__get_node_path_from_id(parent_id)
            assert parent_path is not None
            assert len(parent_path) / 2 <= 252
            self.__node_add_n_children(parent_id, 1)

        # Add a new node into the tree.
        table    = self._table_map['fs_tree']
        insert   = table.insert()
        bin_path = hex_path2bin_path(parent_path + '00000000')
        result   = insert.execute(path = bin_path)
        assert result is not None
        node_id  = result.last_inserted_ids()[0]

        # Assign the correct path to the new node.
        path     = parent_path + int2hex(node_id, 8)
        bin_path = hex_path2bin_path(path)
        depth    = len(path) / 8
        update   = table.update(table.c.id == node_id)
        result   = update.execute(path = bin_path, depth = depth)
        assert result is not None

        # Add a link to every ancestor of the new node into a map.
        while parent_path is not '':
            parent_id = string.atol(parent_path[-8:], 16)
            #print "Path:", parent_path[-8:], "ID:", parent_id
            #print 'Mapping', path_id, 'to', parent_id
            insert = self._table_map['fs_tree_ancestor_map'].insert()
            result = insert.execute(node_id     = node_id,
                                    ancestor_id = parent_id)
            assert result is not None
            parent_path = parent_path[0:len(parent_path) - 8]

        transaction.commit()
        return node_id


    def __remove_node_from_id(self, id):
        assert id is not None
        table  = self._table_map['fs_tree']
        delete = table.delete(table.c.id == id)
        result = delete.execute()
        assert result is not None
        return True


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

        node_id = self.__add_node(parent_id)
        assert node_id is not None

        tbl_f  = self._table_map['fs_dir']
        insert = tbl_f.insert()
        result = insert.execute(node_id       = node_id,
                                name          = directory.get_name(),
                                documentation = directory.get_docs())
        assert result is not None
        directory_id = result.last_inserted_ids()[0]

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
        table  = self._table_map['fs_dir']
        select = table.select(table.c.id == id)
        result = select.execute()
        assert result is not None
        row = result.fetchone()
        if row is None: return None
        directory = Directory(row[table.c.name])
        directory.set_id(id)
        directory.set_docs(row[table.c.documentation])
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
        # Look up the node id.
        table  = self._table_map['fs_dir']
        select = table.select(table.c.id == id)
        result = select.execute()
        assert result is not None
        row = result.fetchone()
        if row is None: return None
        return self.__remove_node_from_id(row['node_id'])


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

        node_id = self.__add_node(parent_id)
        assert node_id is not None

        tbl_f  = self._table_map['fs_file']
        insert = tbl_f.insert()
        result = insert.execute(node_id       = node_id,
                                name          = file.get_name(),
                                documentation = file.get_docs())
        assert result is not None
        file_id = result.last_inserted_ids()[0]

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
        assert id is not None
        tbl_f = self._table_map['fs_file']
        table = tbl_f
        
        tbl_m = self._table_map['fs_tree_ancestor_map']
        table = table.outerjoin(tbl_m, tbl_m.c.ancestor_id == tbl_f.c.node_id)
        
        tbl_t = self._table_map['fs_tree']
        table = table.outerjoin(tbl_t, tbl_m.c.node_id == tbl_t.c.id)
        
        tbl_c = self._table_map['source_chunk']
        table = table.outerjoin(tbl_c, tbl_m.c.node_id == tbl_c.c.node_id)

        tbl_class = self._table_map['api_class']
        table     = table.outerjoin(tbl_class,
                                    tbl_class.c.source_chunk_id == tbl_c.c.id)

        tbl_func  = self._table_map['api_function']
        table     = table.outerjoin(tbl_func,
                                    tbl_func.c.source_chunk_id == tbl_c.c.id)

        select = table.select(tbl_f.c.id == id, use_labels = True)
        result = select.execute(order_by = [desc(tbl_t.c.path)])
        assert result is not None

        row = result.fetchone()
        if row is None: return False
        file = File(row[tbl_f.c.name])
        file.set_id(id)
        file.set_docs(row[tbl_f.c.documentation])

        # Walk through all children, build the object tree.
        last_chunk   = file
        parent_stack = []
        while True:
            if row[tbl_m.c.node_id] is None:
                break

            # Determine the chunk type.
            if row[tbl_class.c.id] is not None:
                chunk = Class(row[tbl_c.c.data], row[tbl_c.c.name])
            elif row[tbl_func.c.id] is not None:
                chunk = Function(row[tbl_c.c.data], row[tbl_c.c.name])
            else:
                chunk = Chunk(row[tbl_c.c.data])
            chunk.set_docs(row[tbl_c.c.documentation])

            # Determine which item is the parent. (=solve indent)
            print "Depth:", row[tbl_t.c.depth]
            if row[tbl_t.c.depth] > len(parent_stack):
                parent_stack.append[last_chunk]
            while row[tbl_t.c.depth] < len(parent_stack):
                parent_stack.pop()

            # Add the current item into the tree.
            parent_stack[-1].add_child(chunk)

            last_chunk = chunk
            row = result.fetchone()
            if row is None: break

        return file


    def remove_file_from_id(self, id):
        """
        Removes the file with the given id from the database.

        @type  id: int
        @param id: The id of the file that is deleted.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        # Look up the node id.
        table  = self._table_map['fs_file']
        select = table.select(table.c.id == id)
        result = select.execute()
        assert result is not None
        row = result.fetchone()
        if row is None: return None
        return self.__remove_node_from_id(row['node_id'])


    def remove_file(self, file):
        """
        Removes the given file from the database.

        @type  file: File
        @param file: The file that is deleted.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        return self.remove_file_from_id(file.get_id())


    def add_chunk(self, parent_id, chunk):
        """
        Adds the given source chunk into the database.

        @type  parent_id: int
        @param parent_id: The id of the chunk under which the new
                          chunk is added.
        @type  chunk: Chunk
        @param chunk: The chunk that is deleted.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert parent_id is not None
        assert chunk     is not None
        connection  = self.db.connect()
        transaction = connection.begin()

        node_id = self.__add_node(parent_id)
        assert node_id is not None

        table  = self._table_map['source_chunk']
        insert = table.insert()
        result = insert.execute(node_id       = node_id,
                                name          = chunk.get_name(),
                                data          = chunk.get_string(),
                                documentation = file.get_docs())
        assert result is not None
        chunk_id = result.last_inserted_ids()[0]

        transaction.commit()
        chunk.set_id(chunk_id)
        return True


if __name__ == '__main__':
    import unittest
    import MySQLdb
    from ConfigParser import RawConfigParser

    class ApiDBTest(unittest.TestCase):
        def test_with_db(self, db):
            assert db is not None
            db = ApiDB(db)
            assert db.uninstall()
            assert db.install()

            # Directories.
            dir = Directory('/')
            assert db.add_directory(None, dir)
            assert db.remove_directory(dir)
            assert db.add_directory(None, dir)
            dir2 = db.get_directory_from_id(dir.get_id())
            assert dir.get_name() == dir2.get_name()

            subdir = Directory('mysubdir')
            assert db.add_directory(dir.get_id(), subdir)
            assert db.remove_directory(subdir)
            assert db.add_directory(dir.get_id(), subdir)
            subdir2 = db.get_directory_from_id(subdir.get_id())
            assert subdir.get_name() == subdir2.get_name()
            
            # Files.
            file = File('lala.py')
            assert db.add_file(dir.get_id(), file)
            assert db.remove_file(file)
            assert db.add_file(dir.get_id(), file)
            file2 = db.get_file_from_id(file.get_id())

            # Classes.
            #FIXME

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

    testcase = ApiDBTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
