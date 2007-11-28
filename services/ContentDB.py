from Content    import Content
from ContentBox import ContentBox

class ContentDB(object):
    def __init__(self, guard):
        self.__guard        = guard
        self.__system_pages = ['homepage', 'default']
        

    def is_system_page_handle(self, content_handle):
        for handle in self.__system_pages:
            if (content_handle + '/').startswith(handle + '/'):
                return True
        return False


    def get(self, handle):
        return self.__guard.get_resource(handle = handle, type = Content)


    def get_responsible_page(self, handle):
        """
        Returns the Content that is responsible for drawing the given
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


    def add(self, parent, content, extension):
        content.set_attribute('recursive', True) #FIXME
        return self.__guard.add_resource(parent, content)


    def save(self, content):
        return self.__guard.save_resource(content)


    def delete(self, content):
        #FIXME: Check the permission of the caller.
        return self.__guard.delete_resource(content)


    def create_box(self):
        box = ContentBox(self, 'content_box')
        self.add(None, box)
        return box


    def get_box(self, id):
        return self.__guard.get_resource(id = id, type = ContentBox)
