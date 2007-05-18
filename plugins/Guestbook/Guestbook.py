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

class Guestbook:
    """
    A Guestbook represents a list of postings.
    """
    def __init__(self, title, descr = ''):
        """
        Instantiates a new Guestbook.
        
        @type  title: string
        @param title: A one-line description of the Guestbook.
        @type  descr: string
        @param descr: A more complete description of the Guestbook.
        @rtype:  Guestbook
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
        @return: The database id of the guestbook.
        """
        self.__id = int(id)


    def get_id(self):
        """
        Returns the database id of the guestbook.
        
        @rtype:  integer
        @return: The database id, or -1 if the guestbook is not yet saved.
        """
        return self.__id


    def set_title(self, title):
        """
        Defines the title of the Guestbook to be added into the database.
        
        @type  title: string
        @param title: The title of the guestbook.
        """
        assert title is not None
        assert len(title) > 0
        self.__title = title


    def get_title(self):
        """
        Returns the title of the guestbook in the database.
        
        @rtype:  string
        @return: The name of the guestbook, or None if undefined.
        """
        return self.__title


    def set_description(self, descr):
        """
        Defines the description of the guestbook.
        
        @type  descr: string
        @param descr: The description of the guestbook.
        """
        self.__descr = descr


    def get_description(self):
        """
        Returns the description of the guestbook.
        
        @rtype:  string
        @return: The description of the guestbook.
        """
        return self.__descr


    def set_datetime(self, added):
        """
        Sets the time when this guestbook was created.
        
        @type:  datetime
        @param: The time when this guestbook was created.
        """
        assert added is not None
        self.__added = added


    def get_datetime(self):
        """
        Returns the time when this guestbook was created.
        
        @rtype:  datetime
        @return: The time when this guestbook was created.
        """
        return self.__added


if __name__ == '__main__':
    import unittest

    class GuestbookTest(unittest.TestCase):
        def runTest(self):
            title = "my guestbook"
            descr = "this is the long description. it is not actually long."
            guestbook = Guestbook(title, descr)
            assert guestbook.get_id()          == -1
            assert guestbook.get_title()       == title
            assert guestbook.get_description() == descr
            
            newid = 123
            guestbook.set_id(newid)
            assert guestbook.get_id() == newid

            new_title = "New Name"
            new_descr = "New Description"
            guestbook.set_title(new_title)
            guestbook.set_description(new_descr)
            assert guestbook.get_title()       == new_title
            assert guestbook.get_description() == new_descr

    testcase = GuestbookTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
