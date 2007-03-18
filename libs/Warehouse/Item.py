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
import os
import mimetypes
from tempfile import mkstemp

class Item:
    """
    An Item represents a single version of a file in the database.
    """
    def __init__(self, alias):
        """
        Instantiates a new Item.
        
        @type  alias: string
        @param alias: The alias of the Item in the database.
        @rtype:  Item
        @return: The new instance.
        """
        assert alias is not None
        assert len(alias) > 0
        self.__id             = -1
        self.__alias          = alias
        self.__filename       = None
        self.__source_file    = None
        self.__move_on_add    = False
        self.__mime_type      = None
        self.__revision       = None
        self.__attribute_dict = {}


    def set_id(self, id):
        """
        Defines the database id. The given id is NOT stored in the database
        (but read from it); the database will assign a new id automatically.
        
        @rtype:  integer
        @return: The database id of the item.
        """
        self.__id = int(id)


    def get_id(self):
        """
        Returns the database id of the Item.
        
        @rtype:  integer
        @return: The database id, or -1 if the Item is not yet saved.
        """
        return self.__id


    def set_alias(self, alias):
        """
        Defines the alias of the Item to be added into the database. The alias
        is the unique name that can be used to look up all revisions of an item
        later.
        
        @type  alias: string
        @param alias: The alias of the file in the database.
        """
        assert alias is not None
        assert len(alias) > 0
        self.__alias = alias


    def get_alias(self):
        """
        Returns the alias of the file in the database.
        
        @rtype:  string
        @return: The name of the file, or None if undefined.
        """
        return self.__alias


    def set_filename(self, filename):
        """
        Defines the filename under which the file in the database can be
        accessed.
        This method should normally not be used, you probably want
        set_source_file() instead.
        
        @type  filename: string
        @param filename: The name of the file in the database.
        """
        self.__filename = filename


    def get_filename(self):
        """
        Returns the filename under which the file in the database can be
        accessed.
        
        @rtype:  string
        @return: The name of the file, or None if not yet stored.
        """
        return self.__filename


    def set_source_filename(self, source_file, move = False, magic = True):
        """
        Defines the name of the file to be added into the database.
        Note that detecting the mime type automatically is expensive.
        
        @type  source_file: string
        @param source_file: The name of the file to be added.
        @type  move: boolean
        @param move: When True, the file is *moved* instead of copied when the
                     item is added into the database.
        @type  magic: boolean
        @param magic: When True, the mime type is automatically determined.
        """
        assert os.path.exists(source_file)
        # Determine MIME type.
        if magic:
            self.__mime_type = mimetypes.guess_type(source_file)[0]
        else:
            self.__mime_type = None
        self.__source_file = source_file
        self.__move_on_add = move


    def get_source_filename(self):
        """
        Returns the name of the file that will be added into the database.
        
        @rtype:  string
        @return: The name of the file, or None if undefined.
        """
        return self.__source_file


    def set_content(self, content, magic = True):
        """
        If you have the data in memory instead of a file, you can use this
        method instead of set_source_file(). It takes the content, creates a file
        out of it, and when the item is added into the database, moves the
        temporary file into the database.
        
        @type  content: string
        @param content: The content of the item.
        @type  magic: boolean
        @param magic: When True, the mime type is automatically determined.
        """
        # Write the content into a temporary file.
        (fp, temp_file_name) = mkstemp('txt', '/tmp/')
        os.write(fp, content)
        os.close(fp)
        self.set_source_filename(temp_file_name, True, magic)


    def get_move_on_add(self):
        """
        Returns True if the file returned by get_source_file() will be moved when
        the item is added into the database.
        Returns False if the file will be copied.
        
        @rtype:  boolean
        @return: Whether the file will be moved.
        """
        return self.__move_on_add


    def set_revision(self, revision):
        """
        Defines the revision number. The given version number is NOT stored
        in the database, because the database will always use the
        last_revision_number + 1.
        
        @type  revision: integer
        @param revision: The revision number of the item.
        """
        assert revision is not None
        self.__revision = revision


    def get_revision(self):
        """
        Returns the revision number of the object.
        
        @rtype:  integer
        @return: The revision number, or None if the Item is not yet saved.
        """
        return self.__revision


    def set_mime_type(self, mime_type):
        """
        Can be used to overwrite the mime type. Should normally not be used,
        because the mime type is detected automatically when
        set_source_filename() or set_content() is used.
        
        @type  mime_type: string
        @param mime_type: The mime type.
        """
        self.__mime_type = mime_type


    def get_mime_type(self):
        """
        Returns the mime type of the Item, for example "txt/html".
        
        @rtype:  string
        @return: The mime type or None if unknown.
        """
        return self.__mime_type


    def set_attribute(self, *args, **kwargs):
        """
        You can add metadata to any revision of an item in the database. For
        example, when adding a video you might want to append tags such as
        "comedy, politics".
        
        Use this method to pass the metadata that is saved and attached to
        the new revision. Supported value types are integer, boolean, and
        strings with a length up to 200 characters.
        
        @type  keyword_list: dict
        @param keyword_list: The attributes to be stored with the revision.
        """
        self.__attribute_dict.update(kwargs)


    def get_attribute(self, name):
        """
        Returns the value of the attribute with the given name.
        
        @rtype:  string
        @return: The attribute name, or None of it does not exist.
        """
        return self.__attribute_dict.get(name, None)


    def remove_attribute(self, name):
        """
        Removes the attribute with the given name.
        
        @type  name: string
        @param name: The attribute name.
        """
        if self.__attribute_dict.has_key(name):
            del self.__attribute_dict[name]


    def removes_attributes(self):
        """
        Removes all current attributes.
        """
        self.__attribute_dict = {}


    def get_attribute_dict(self):
        """
        Returns a dictionary containing all attributes.
        
        @rtype: dict
        @return: A list of all attributes.
        """
        return self.__attribute_dict


if __name__ == '__main__':
    import unittest

    class ItemTest(unittest.TestCase):
        def runTest(self):
            alias = "my/alias/is/whatever"
            item  = Item(alias)
            assert item.get_id()    == -1
            assert item.get_alias() == alias
            
            test_file = 'test.py'
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

    testcase = ItemTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
