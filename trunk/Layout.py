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
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'libs'))
from genshi.input import XML

class Layout:
    def __init__(self, integrator, page):
        """
        If the given page has no layout defined, a default layout is used.
        """
        assert integrator is not None
        assert page       is not None
        self.__extension_handles = []
        self.__extensions        = []
        self.__integrator        = integrator
        self.__descriptor        = page.get_attribute('extension')

        # If a layout was not defined, use a default layout.
        layout = page.get_attribute('layout')
        if layout is not None and layout == '':
            self.__layout = XML(layout)
        else:
            assert self.__descriptor is not None
            layout  = '<table class="layout"><tbody><tr><td>'
            layout += '<table><tbody><tr><td>'
            layout += self.__descriptor
            layout += '</td></tr></tbody></table>'
            layout += '</td></tr></tbody></table>'
            self.__layout = XML(layout)
        self.__parse()


    def __parse(self):
        handles = self.__layout.select('tbody/tr/td/table/tbody/tr/td/text()')
        for kind, data, pos in handles:
              self.__extension_handles.append(data)


    def __load_extensions(self):
        if len(self.__extension_handles) == len(self.__extensions):
            return
        self.__extensions = []
        for handle in self.__extension_handles:
            integrator = self.__integrator
            extension  = integrator.load_extension_from_descriptor(handle)
            assert extension is not None
            self.__extensions.append(extension)


    def get_extension_handles(self):
        return self.__extension_handles


    def render(self):
        self.__load_extensions()
        #FIXME: Render an actual layout rather than just firing all extensions
        #sequentially.
        for extension in self.__extensions:
            extension.on_render_request()


if __name__ == '__main__':
    import unittest
    from Guard import Resource

    class LayoutTest(unittest.TestCase):
        def runTest(self):
            layout = '''
<table><tbody>
  <tr>
    <td>
      <table><tbody>
        <tr>
          <td>Test 1/1</td>
          <td></td>
          <td>Test 1/3</td>
        </tr>
        <tr>
          <td rowspan="2">Test 2/1</td>
          <td colspan="2">Test 2/2</td>
        </tr>
        <tr>
          <td rowspan="1">Test 3/2</td>
          <td colspan="2">Test 3/3</td>
        </tr>
      </tbody></table>
    </td>
  </tr>
</tbody></table>'''
            page = Resource('my resource')
            page.set_attribute('layout',    layout)
            page.set_attribute('extension', 'my_extension>=1.0')
            layout = Layout(object, page)
            assert layout is not None

    testcase = LayoutTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
