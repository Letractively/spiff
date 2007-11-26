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
from LayoutParser import LayoutParser

class Layout:
    def __init__(self, integrator, extension_api, page):
        """
        If the given page has no layout defined, a default layout is used.
        """
        assert integrator    is not None
        assert extension_api is not None
        assert page          is not None
        self.__integrator    = integrator
        self.__extension_api = extension_api
        self.__descriptor    = page.get_attribute('extension')
        self.__layout        = page.get_attribute('layout')

        # If a layout was not defined, use a default layout.
        if self.__layout is None or self.__layout == '':
            assert self.__descriptor is not None
            self.__layout  = '<t cl="layout"><r><c>'
            self.__layout += '<t><r><c>'
            self.__layout += self.__descriptor
            self.__layout += '</c></r></t>'
            self.__layout += '</c></r></t>'

        self.__layout_parser = LayoutParser(self.__layout)
        self.__layout_parser.set_data_handler(self._layout_data_handler)


    def _layout_data_handler(self, data):
        extension = self.__integrator.load_package_from_descriptor(data)
        assert extension is not None
        extension.on_render_request()
        output = self.__extension_api.get_output()
        self.__extension_api.clear_output()
        return output


    def render(self):
        self.__layout_parser.parse()
        print self.__layout_parser.html


if __name__ == '__main__':
    import unittest
    from Guard import Resource

    class LayoutTest(unittest.TestCase):
        def runTest(self):
            layout = '''
<t>
  <r>
    <c>
      <t>
        <r>
          <c>Test 1/1</c>
          <c></c>
          <c>Test 1/3</c>
        </r>
        <r>
          <c rows="2">Test 2/1</c>
          <c cols="2">Test 2/2</c>
        </r>
        <r>
          <c rows="1">Test 3/2</c>
          <c cols="2">Test 3/3</c>
        </r>
      </t>
    </c>
  </r>
</t>'''
            page = Resource('my resource')
            page.set_attribute('layout',    layout)
            page.set_attribute('extension', 'my_extension>=1.0')
            layout = Layout(object, object, page)
            assert layout is not None

    testcase = LayoutTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
