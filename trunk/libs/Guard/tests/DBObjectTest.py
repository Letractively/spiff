import sys, unittest, re
sys.path.insert(0, '..')

def suite():
    tests = ['testDBObject']
    return unittest.TestSuite(map(DBObjectTest, tests))

from functions import make_handle_from_string
from DBObject  import DBObject

class DBObjectTest(unittest.TestCase):
    def testDBObject(self):
        name   = "Test DBObject"
        dbobject = DBObject(name)
        assert dbobject.get_id() is None
        assert dbobject.get_name()   == name
        assert dbobject.get_handle() == make_handle_from_string(name)
        
        handle = "myhandle"
        dbobject = DBObject(name, handle)
        assert dbobject.get_id() is None
        assert dbobject.get_name()   == name
        assert dbobject.get_handle() == handle

        newid = 123
        dbobject.set_id(newid)
        assert dbobject.get_id() == newid

        newname = "New Name"
        dbobject.set_name(newname)
        assert dbobject.get_name()   == newname
        assert dbobject.get_handle() == handle

        newhandle = "newhandle"
        dbobject.set_handle(newhandle)
        assert dbobject.get_name()   == newname
        assert dbobject.get_handle() == newhandle

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
