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
        self.__add_table(Table(pfx + 'source_tree', metadata,
            Column('id',              Integer,     primary_key = True),
            Column('path',            Binary(255), unique = True),
            Column('depth',           Integer),
            Column('n_children',      Integer),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'source_tree_ancestor_map', metadata,
            Column('node_id',     Integer),
            Column('ancestor_id', Integer),
            ForeignKeyConstraint(['node_id'],
                                 ['source_tree.id'],
                                 ondelete = 'CASCADE'),
            ForeignKeyConstraint(['ancestor_id'],
                                 ['source_tree.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'source_chunk', metadata,
            Column('id',            Integer, primary_key = True),
            Column('node_id',       Integer),
            Column('type',          String(230)),
            Column('data',          TEXT),
            Column('name',          String(230)),
            ForeignKeyConstraint(['node_id'],
                                 ['source_tree.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'api_doc', metadata,
            Column('id',                 Integer, primary_key = True),
            Column('source_chunk_id',    Integer),
            Column('documents_chunk_id', Integer),
            Column('introduction',       String(230)),
            Column('description',        TEXT),
            ForeignKeyConstraint(['documents_chunk_id'],
                                 ['source_chunk.id'],
                                 ondelete = 'CASCADE'),
            ForeignKeyConstraint(['source_chunk_id'],
                                 ['source_chunk.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'argument', metadata,
            Column('id',         Integer, primary_key = True),
            Column('api_doc_id', Integer),
            Column('name',       String(100)),
            Column('type',       String(100)),
            Column('docs',       TEXT),
            ForeignKeyConstraint(['api_doc_id'],
                                 ['api_doc.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'return_value', metadata,
            Column('id',         Integer, primary_key = True),
            Column('api_doc_id', Integer),
            Column('type',       String(100)),
            Column('docs',       TEXT),
            ForeignKeyConstraint(['api_doc_id'],
                                 ['api_doc.id'],
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
        delete = self._table_map['source_tree'].delete()
        result = delete.execute()
        assert result is not None
        return True


    def __get_node_id_from_chunk_id(self, id):
        assert id is not None
        table  = self._table_map['source_chunk']
        query  = select([table.c.node_id],
                        table.c.id == id,
                        from_obj = [table])
        result = query.execute()
        assert result is not None
        row = result.fetchone()
        if not row: return None
        return row[table.c.node_id]


    def __get_node_path_from_id(self, id):
        assert id is not None
        table  = self._table_map['source_tree']
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
        table  = self._table_map['source_tree']
        update = table.update(table.c.id == id)
        result = update.execute(n_children = table.c.n_children + n_children)
        assert result is not None


    def __add_node(self, parent_id):
        connection = self.db.connect()
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
        table    = self._table_map['source_tree']
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
            insert = self._table_map['source_tree_ancestor_map'].insert()
            result = insert.execute(node_id     = node_id,
                                    ancestor_id = parent_id)
            assert result is not None
            parent_path = parent_path[0:len(parent_path) - 8]

        transaction.commit()
        connection.close()
        return node_id


    def __remove_node_from_id(self, id):
        assert id is not None
        table  = self._table_map['source_tree']
        delete = table.delete(table.c.id == id)
        result = delete.execute()
        assert result is not None
        return True


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
        assert chunk is not None
        connection  = self.db.connect()
        transaction = connection.begin()

        node_id = self.__add_node(parent_id)
        assert node_id is not None

        table  = self._table_map['source_chunk']
        insert = table.insert()
        result = insert.execute(node_id = node_id,
                                type    = chunk.get_type(),
                                data    = chunk.data,
                                name    = chunk.get_name())
        assert result is not None
        chunk_id = result.last_inserted_ids()[0]

        if chunk.get_type() == 'api_doc':
            # Insert documentation, if any.
            table  = self._table_map['api_doc']
            insert = table.insert()
            result = insert.execute(source_chunk_id = chunk_id,
                                    documents_chunk_id = chunk_id, #FIXME
                                    introduction    = chunk.get_introduction(),
                                    description     = chunk.get_description())
            assert result is not None
            api_doc_id = result.last_inserted_ids()[0]

            # Insert argument documentation, if any.
            for arg in chunk.get_argument_list():
                table  = self._table_map['argument']
                insert = table.insert()
                result = insert.execute(api_doc_id = api_doc_id,
                                        name       = arg.get_name(),
                                        type       = arg.get_type(),
                                        docs       = arg.get_docs())
                assert result is not None

            # Insert return type documentation, if any.
            return_var = chunk.get_return()
            if return_var is not None:
                table  = self._table_map['return_value']
                insert = table.insert()
                result = insert.execute(api_doc_id = api_doc_id,
                                        type       = return_var.get_type(),
                                        docs       = return_var.get_docs())
                assert result is not None

        for child in chunk.get_child_list():
            self.add_chunk(chunk_id, child)

        transaction.commit()
        connection.close()
        chunk.set_id(chunk_id)
        return True


    def get_chunk_from_id(self, id):
        """
        Returns the chunk with the given id from the database, including
        all of it's children.

        @type  id: int
        @param id: The id of the wanted chunk.
        @rtype:  Chunk
        @return: The Chunk instance on success, None otherwise.
        """
        assert id is not None
        tbl_c1 = self._table_map['source_chunk'].alias('c1')
        table  = tbl_c1

        tbl_m  = self._table_map['source_tree_ancestor_map']
        table  = table.outerjoin(tbl_m, tbl_c1.c.node_id == tbl_m.c.ancestor_id)

        tbl_t  = self._table_map['source_tree']
        table  = table.outerjoin(tbl_t, tbl_m.c.node_id == tbl_t.c.id)
        
        tbl_c2 = self._table_map['source_chunk'].alias('c2')
        table  = table.outerjoin(tbl_c2, tbl_m.c.node_id == tbl_c2.c.node_id)
        
        select = table.select(tbl_c1.c.id == id, use_labels = True)
        result = select.execute(order_by = [desc(tbl_t.c.path)])
        assert result is not None

        row = result.fetchone()
        if row is None: return False
        chunk = Chunk(row[tbl_c1.c.type],
                      row[tbl_c1.c.data],
                      row[tbl_c1.c.name])
        chunk.set_id(row[tbl_c1.c.id])

        # Walk through all children, build the object tree.
        last_chunk   = chunk
        parent_stack = []
        while True:
            if row[tbl_m.c.node_id] is None:
                break

            child = Chunk(row[tbl_c2.c.type],
                          row[tbl_c2.c.data],
                          row[tbl_c2.c.name])
            child.set_id(row[tbl_c2.c.id])

            # Determine which item is the parent. (=solve indent)
            #print "Depth:", row[tbl_t.c.depth]
            if row[tbl_t.c.depth] > len(parent_stack):
                parent_stack.append(last_chunk)
            while row[tbl_t.c.depth] < len(parent_stack):
                parent_stack.pop()

            # Add the current item into the tree.
            parent_stack[-1].add_child(child)

            last_chunk = child
            row = result.fetchone()
            if row is None: break

        return chunk


    def remove_chunk_from_id(self, id):
        """
        Removes the chunk with the given id from the database.

        @type  id: int
        @param id: The id of the chunk that is to be deleted.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        node_id = self.__get_node_id_from_chunk_id(id)
        assert node_id is not None
        return self.__remove_node_from_id(node_id)


    def remove_chunk(self, chunk):
        """
        Removes the given chunk from the database.

        @type  file: Chunk
        @param file: The chunk that is to be deleted.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        return self.remove_chunk_from_id(chunk.get_id())


if __name__ == '__main__':
    import unittest
    import MySQLdb
    from ConfigParser import RawConfigParser
    import Python

    class ApiDBTest(unittest.TestCase):
        def test_with_db(self, db):
            assert db is not None
            db = ApiDB(db)
            assert db.uninstall()
            assert db.install()

            # Directories.
            dir = Directory('/')
            assert db.add_chunk(None, dir)
            assert db.remove_chunk(dir)
            assert db.add_chunk(None, dir)
            dir2 = db.get_chunk_from_id(dir.get_id())
            assert dir.get_name() == dir2.get_name()

            subdir = Directory('mysubdir')
            assert db.add_chunk(dir.get_id(), subdir)
            assert db.remove_chunk(subdir)
            assert db.add_chunk(dir.get_id(), subdir)
            subdir2 = db.get_chunk_from_id(subdir.get_id())
            assert subdir.get_name() == subdir2.get_name()
            
            # Files.
            file = File('lala.py')
            assert db.add_chunk(dir.get_id(), file)
            assert db.remove_chunk(file)
            assert db.add_chunk(dir.get_id(), file)
            file2 = db.get_chunk_from_id(file.get_id())

            # Chunks.
            chunk = Chunk('text', 'whatever.this = maybe')
            assert db.add_chunk(file.get_id(), chunk)

            # Read an entire file into one string.
            filename = 'Python/testfile.py'
            infile   = open(filename, 'r')
            in_str   = infile.read()
            infile.close()

            # Insert some real world data.
            assert db.clear_database()
            reader = Python.Reader()
            chunk  = reader.read(filename)
            assert chunk is not None
            assert chunk.get_data() == in_str
            assert db.add_chunk(None, chunk)
            
            # Check whether the data is still complete if we load it from
            # the database.
            chunk = db.get_chunk_from_id(chunk.get_id())
            assert chunk.get_data() == in_str

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
