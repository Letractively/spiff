from Page    import Page
from PageBox import PageBox

class PageDB(object):
    def __init__(self, guard):
        self.__guard        = guard
        self.__system_pages = ['homepage', 'default']
        

    def is_system_page_handle(self, page_handle):
        for handle in self.__system_pages:
            if (page_handle + '/').startswith(handle + '/'):
                return True
        return False


    def get(self, handle):
        return self.__guard.get_resource(handle = handle, type = Page)


    def get_responsible_page(self, handle):
        """
        Returns the Page that is responsible for drawing the given
        page.
        """
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
        #FIXME: Check the permission of the caller.
        return self.__guard.delete_resource(page)


    def create_box(self):
        box = PageBox(self, 'page_box')
        self.add(None, box)
        return box


    def get_box(self, id):
        return self.__guard.get_resource(id = id, type = PageBox)
