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

class Renderer:
    def __init__(self):
        self.__app_name    = 'Spiff Application'
        self.__app_version = '0.1'


    def set_app_name(self, app_name):
        assert app_name is not None
        self.__app_name = app_name


    def get_app_name(self):
        return self.__app_name


    def set_app_version(self, app_version):
        assert app_version is not None
        self.__app_version = app_version


    def get_app_version(self):
        return self.__app_version


    def section_start(self, message):
        """
        Increases paragraph depth.
        """
        assert False  # Must be implemented!


    def section_end(self):
        """
        Decreases paragraph depth.
        """
        assert False  # Must be implemented!


    def task_done(self, message, result):
        assert False  # Must be implemented!
