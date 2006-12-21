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

class Environment:
    def __init__(self):
        self._app_name    = 'Spiff Application'
        self._app_version = '0.1'


    def get_initial_task_path(self):
        return [0]


    def set_app_name(self, app_name):
        assert app_name is not None
        self._app_name = app_name


    def get_app_name(self):
        return self._app_name


    def set_app_version(self, app_version):
        assert app_version is not None
        self._app_version = app_version


    def get_app_version(self):
        return self._app_version


    def start(self):
        pass


    def end(self):
        pass


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


    def task_done(self, message, result, hint = ''):
        assert False  # Must be implemented!


    def show_form(self, form):
        """
        This function renders the given form.
        Returns True if the result is already available (=the method is
        synchronous), False otherwise (=the method is asynchronous).
        If the result is asynchronous, the Task that triggered the method
        needs to defer any further action until the Constructor is
        re-instantiated at a time where the result can be taken.
        
        This is especially important for stateless protocols like in a Web UI,
        where the result of a form can only be retrieved when the client
        contacts the server for another web page.
        """
        assert False  # Must be implemented!


    def get_form_data(self):
        assert False  # Must be implemented!
