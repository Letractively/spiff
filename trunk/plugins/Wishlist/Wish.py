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

class Wish:
    """
    A Wish represents a single entry in the wishlist.
    """
    def __init__(self, title, descr = ''):
        """
        Instantiates a new Wish.
        
        @type  title: string
        @param title: A one-line description of the Wish.
        @type  descr: string
        @param descr: A more complete description of the Wish.
        @rtype:  Wish
        @return: The new instance.
        """
        assert title is not None
        assert len(title) > 0
        assert descr is not None
        self.__id    = -1
        self.__title = title
        self.__descr = descr
        self.__added = None


    def set_id(self, id):
        """
        Defines the database id. The given id is NOT stored in the database
        (but read from it); the database will assign a new id automatically.
        
        @rtype:  integer
        @return: The database id of the wish.
        """
        self.__id = int(id)


    def get_id(self):
        """
        Returns the database id of the Wish.
        
        @rtype:  integer
        @return: The database id, or -1 if the Wish is not yet saved.
        """
        return self.__id


    def set_title(self, title):
        """
        Defines the title of the Wish to be added into the database.
        
        @type  title: string
        @param title: The title of the wish.
        """
        assert title is not None
        assert len(title) > 0
        self.__title = title


    def get_title(self):
        """
        Returns the title of the wish in the database.
        
        @rtype:  string
        @return: The name of the file, or None if undefined.
        """
        return self.__title


    def set_description(self, descr):
        """
        Defines the description of the wish.
        
        @type  descr: string
        @param descr: The description of the wish.
        """
        self.__descr = descr


    def get_description(self):
        """
        Returns the description of the wish.
        
        @rtype:  string
        @return: The description of the wish.
        """
        return self.__descr


    def set_datetime(self, added):
        """
        Sets the time when this wish was created.
        
        @type:  datetime
        @param: The time when this wish was created.
        """
        assert added is not None
        self.__added = added


    def get_datetime(self):
        """
        Returns the time when this wish was created.
        
        @rtype:  datetime
        @return: The time when this wish was created.
        """
        return self.__added


if __name__ == '__main__':
    import unittest

    class WishlistTest(unittest.TestCase):
        def runTest(self):
            title = "my wish be your command"
            descr = "this is the long description. it is not actually long."
            wish  = Wish(title, descr)
            assert wish.get_id()          == -1
            assert wish.get_title()       == title
            assert wish.get_description() == descr
            
            newid = 123
            wish.set_id(newid)
            assert wish.get_id() == newid

            new_title = "New Name"
            new_descr = "New Description"
            wish.set_title(new_title)
            wish.set_description(new_descr)
            assert wish.get_title()       == new_title
            assert wish.get_description() == new_descr

    testcase = WishlistTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
