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
from Renderer import Renderer

class WebRenderer(Renderer):
    def __init__(self, genshi = None):
        Renderer.__init__(self)
        # FIXME: if not genshi:
        self.__genshi = genshi
        self.__level  = 1


    def __open_table(self):
        genshi.append('<table>')
        self.__table_open = True


    def __close_table(self):
        genshi.append('</table>')
        self.__table_open = False


    def section_start(self, message):
        if self.__table_open:
            self.__close_table()
        self.__level += 1
        tag_name = 'h' + self.__level + ''
        genshi.append('<' + tag_name + '>' + message + '</' + tag_name + '>')
        genshi.append('<p>')


    def section_end(self):
        if self.__table_open:
            self.__close_table()
        self.__level -= 1
        genshi.append('</p>')


    def task_done(self, message, result):
        if not self.__table_open:
            self.__open_table()
        genshi.append('<tr>')
        genshi.append('<td>' + message + '</td>')
        genshi.append('<td>' + result  + '</td>')
        genshi.append('</tr>')

