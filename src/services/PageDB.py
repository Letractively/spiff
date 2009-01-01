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
from objects import Page
from objects import PageAction
from objects import PageBox

class PageDB(object):
    def __init__(self, guard):
        self.__guard        = guard
        self.__system_pages = ['homepage', 'default']
        guard.register_type([Page, PageAction, PageBox])
        

    def is_system_page_handle(self, page_handle):
        if page_handle is None:
            return False
        for handle in self.__system_pages:
            if (page_handle + '/').startswith(handle + '/'):
                return True
        return False


    def get(self, handle):
        return self.__guard.get_resource(handle = handle, type = Page)


    def get_responsible_page(self, handle):
        """
        Returns the Page object that is responsible for drawing the given
        page.
        """
        if handle is None:
            handle = 'default'

        # Attempt to get the page using the path.
        path = handle.split('/')
        while len(path) > 0:
            page = self.get('/'.join(path))
            if page is not None and page.get_attribute('recursive'):
                return page
            path = path[:-1]

        # Ending up here no matching page was found. Try the default page.
        page = self.get('default')
        if page is not None and page.get_attribute('recursive'):
            return page
        return None


    def add(self, parent, page, extension):
        page.set_attribute('recursive', True) #FIXME
        return self.__guard.add_resource(parent, page)


    def save(self, page):
        return self.__guard.save_resource(page)


    def delete(self, page):
        return self.__guard.delete_resource(page)


    def create_box(self):
        box = PageBox(self, 'page_box')
        self.add(None, box)
        return box


    def get_box(self, id):
        return self.__guard.get_resource(id = id, type = PageBox)
