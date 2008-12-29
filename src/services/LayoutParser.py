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
from genshi.input import XML

class LayoutParser(object):
    def __init__(self, xml):
        self.__xml               = XML(xml)
        self.__data_handler      = None
        self.__data_handler_args = None
        self.layout              = xml
        self.html                = ''


    def set_data_handler(self, handler, *args):
        """
        The function given in handler is called whenever data is found in the
        XML. The handler is passed the data (string) as an argument.
        """
        self.__data_handler      = handler
        self.__data_handler_args = args


    def parse(self):
        self.layout = ''
        self.html   = ''
        for kind, data, position in self.__xml:
            if   kind == 'START': self._startElement(data)
            elif kind == 'END':   self._endElement(data)
            elif kind == 'TEXT':  self._characters(data)


    def _startElement(self, data):
        (name, attrs) = data
        if   name == 't': self._start_table(attrs)
        elif name == 'r': self._start_row(attrs)
        elif name == 'c': self._start_cell(attrs)


    def _characters(self, data):
        data = data.strip()
        if data == '':
            return
        if self.__data_handler is not None:
            data = self.__data_handler(data, *self.__data_handler_args)
        self.layout += data
        self.html   += data


    def _endElement(self, name):
        if   name == 't': self._end_table()
        elif name == 'r': self._end_row()
        elif name == 'c': self._end_cell()


    def _start_table(self, attrs):
        self.layout += '<t>'
        self.html   += '<table width="100%"><tbody>'


    def _start_row(self, attrs):
        self.layout += '<r>'
        self.html   += '<tr>'


    def _start_cell(self, attrs):
        self.layout += '<c'
        self.html   += '<td'
        for attribute in attrs:
            key   = attribute[0].encode('latin-1')
            value = attribute[1].encode('latin-1')
            self.layout += ' %s="%s"' % (key, value)
            if key == 'rows':
                key = 'rowspan'
            elif key == 'cols':
                key = 'colspan'
            elif key == 'cl':
                key = 'class'
            self.html += ' %s="%s"' % (key, value)
        self.layout += '>'
        self.html   += '>'


    def _end_cell(self):
        self.layout += '</c>'
        self.html   += '</td>'


    def _end_row(self):
        self.layout += '</r>'
        self.html   += '</tr>'


    def _end_table(self):
        self.layout += '</t>'
        self.html   += '</tbody></table>'


if __name__ == '__main__':
    import unittest
    from genshi.input import XML

    class LayoutParserTest(unittest.TestCase):
        def runTest(self):
            layout = '''
<t>
  <r>
    <c>
      <t>
        <r>
          <c cl="header">Test 1/1</c>
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
            l2h = LayoutParser(layout)
            l2h.parse()
            assert len(l2h.layout) > 100
            assert len(l2h.html) > len(l2h.layout)

    testcase = LayoutParserTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
