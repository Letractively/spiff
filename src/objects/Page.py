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
from SpiffGuard import ResourceGroup
import services

class Page(ResourceGroup):
    def __init__(self, name, handle = None):
        ResourceGroup.__init__(self, name, handle)
        self.__output              = None
        self.__extensions          = None
        self.__non_cacheable_found = False


    def assign_extension(self, handle):
        layout  = '<t cl="layout"><r><c>'
        layout += '<t><r><c>%s</c></r></t>' % handle
        layout += '</c></r></t>'
        self.set_attribute('layout', layout)
        self.__extensions = [handle]


    def __collect_extension_descriptor(self, descriptor):
        self.__extensions.append(descriptor)
        return descriptor


    def __replace_extension_descriptor(self, descriptor, api):
        # Retrieve the extension, but do not yet load it.
        integrator = api.get_integrator()
        package    = integrator.get_package_from_descriptor(descriptor)
        if package is None:
            output = "Whoops... extension %s not found!" % repr(descriptor)
            self.__non_cacheable_found = True
            return output

        if package.check_cache():
            output = api.get_cache().get(descriptor)
            if output is not None:
                return output

        output = package.render()
        if package.get_attribute('cacheable') == True:
            api.get_cache().add(descriptor, output)
        else:
            self.__non_cacheable_found = True
        return output


    def get_extension_handle_list(self):
        if self.__extensions is not None:
            return self.__extensions
        self.__extensions = []
        layout            = self.get_attribute('layout')
        parser            = services.LayoutParser(layout)
        parser.set_data_handler(self.__collect_extension_descriptor)
        parser.parse()
        return self.__extensions


    def get_output(self, extension_api):
        # If this method was already called there is no need to re-parse.
        if self.__output is not None:
            return self.__output

        # Ending up here the page was not cached.
        layout = self.get_attribute('layout')
        parser = services.LayoutParser(layout)
        parser.set_data_handler(self.__replace_extension_descriptor,
                                extension_api)
        parser.parse()
        self.__output = parser.html
        return self.__output


    def is_cacheable(self):
        assert self.__output is not None
        return not self.__non_cacheable_found
