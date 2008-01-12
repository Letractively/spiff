import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'Warehouse'))

def suite():
    tests = ['testDB']
    return unittest.TestSuite(map(DBTest, tests))

import MySQLdb
from sqlalchemy     import create_engine
from sqlalchemy.orm import clear_mappers
from ConfigParser   import RawConfigParser
from DB             import DB
from Item           import Item

class DBTest(unittest.TestCase):
    def setUp(self):
        # Read config.
        cfg = RawConfigParser()
        cfg.read('unit_test.cfg')
        host     = cfg.get('database', 'host')
        db_name  = cfg.get('database', 'db_name')
        user     = cfg.get('database', 'user')
        password = cfg.get('database', 'password')

        # Connect to MySQL.
        auth        = user + ':' + password
        dbn         = 'mysql://' + auth + '@' + host + '/' + db_name
        self.engine = create_engine(dbn)
        clear_mappers()
        self.db     = DB(self.engine)


    def tearDown(self):
        self.assert_(self.db.clear_database())
        self.assert_(self.db.uninstall())


    def testDB(self):
        self.db.set_directory('data')
        self.assert_(self.db.install())

        # Add a revision of a file into the database.
        item = Item("my/alias")
        test_file = os.path.join(os.path.dirname(__file__), 'test.py')
        item.set_source_filename(test_file)
        self.assert_(self.db.add_file(item))
        self.assert_(item.get_revision() == 1)

        # Add another revision of the file into the database.
        test_file = os.path.join(os.path.dirname(__file__), 'test2.py')
        item.set_source_filename(test_file)
        self.assert_(self.db.add_file(item))
        self.assert_(item.get_revision() == 2)

        # Add a new revision, but this time user a string instead of a file.
        item.set_content("this is the new version of test.txt")
        self.assert_(self.db.add_file(item))
        self.assert_(item.get_revision() == 3)

        # Retrieve the latest revision.
        item = self.db.get_file_from_alias("my/alias")
        self.assert_(item.get_revision() == 3)
        #print "Latest revision is", item.get_revision()

        # Retrieve all revisions.
        items = self.db.get_file_list_from_alias("my/alias")
        #print "All revisions:", [item.get_revision() for item in items]
        self.assert_(len(items) == 3)
        self.assert_(items[0].get_revision() == 3)
        self.assert_(items[1].get_revision() == 2)
        self.assert_(items[2].get_revision() == 1)

        # Retrieve revision 2.
        item = self.db.get_file_from_alias("my/alias", 2)
        self.assert_(item.get_revision() == 2)

        # Delete revision 2.
        self.assert_(self.db.remove_file(item))

        # Make sure that it is gone.
        items = self.db.get_file_list_from_alias("my/alias")
        self.assert_(len(items) == 2)
        self.assert_(items[0].get_revision() == 3)
        self.assert_(items[1].get_revision() == 1)

        # Delete the remaining items.
        self.assert_(self.db.remove_files_from_alias("my/alias"))

        # Make sure that they are gone.
        items = self.db.get_file_list_from_alias("my/alias")
        self.assert_(len(items) == 0)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
