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

class CliRenderer(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.__level = 1


    def section_start(self, message):
        for i in range(self.__level):
            print ' ',
        print 'Section', message, 'start.'
        self.__level += 1


    def section_end(self):
        self.__level -= 1
        for i in range(self.__level):
            print ' ',
        print 'Section end.'


    def task_done(self, message, result):
        for i in range(self.__level):
            print ' ',
        print 'Task:', message, '-', result

