import sys, unittest, re
sys.path.insert(0, '..')
sys.path.insert(0, '../..')

def suite():
    tests = ['testDBReader']
    return unittest.TestSuite(map(DBReaderTest, tests))

import MySQLdb
from sqlalchemy     import create_engine
from sqlalchemy.orm import clear_mappers
from ConfigParser   import RawConfigParser
from DBReader       import DBReader

class DBReaderTest(unittest.TestCase):
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

    def testDBReader(self):
        # We only test instantiation here, the other tests
        # are done in DBTest.py.
        db = DBReader(self.engine)
        self.assert_(db is not None)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
