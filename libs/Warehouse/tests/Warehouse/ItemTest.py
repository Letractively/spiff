import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'Warehouse'))

def suite():
    tests = ['testItem']
    return unittest.TestSuite(map(ItemTest, tests))

from Item import Item

class ItemTest(unittest.TestCase):
    def testItem(self):
        alias = "my/alias/is/whatever"
        item  = Item(alias)
        assert item.get_id()    == -1
        assert item.get_alias() == alias
        
        test_file = os.path.join(os.path.dirname(__file__), 'test.py')
        item.set_source_filename(test_file)
        assert item.get_source_filename() == test_file
        assert item.get_mime_type() == 'text/x-python'

        newid = 123
        item.set_id(newid)
        assert item.get_id() == newid

        new_alias = "New Name"
        item.set_alias(new_alias)
        assert item.get_alias() == new_alias

        attr_name  = 'test_attribute'
        attr_value = 'Works'
        item.set_attribute(**{attr_name: attr_value})
        assert item.get_attribute(attr_name) == attr_value
        item.remove_attribute(attr_name)
        assert item.get_attribute(attr_name) is None

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
