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
        self.__attributes = {}


    def set_app_name(self, app_name):
        """
        Defines the application name.
        @type  app_name string
        @param app_name The application name.
        """
        assert app_name is not None
        self._app_name = app_name


    def get_app_name(self):
        """
        Returns the application name.
        @return string
        """
        return self._app_name


    def set_app_version(self, app_version):
        """
        Defines the application version.
        @type  app_version string
        @param app_version The version number.
        """
        assert app_version is not None
        self._app_version = app_version


    def get_app_version(self):
        """
        Returns the application version.
        @return string
        """
        return self._app_version


    def set_attribute(self, name, value):
        """
        This method lets tasks provide arbitrary data to have it carried
        along. This is a way in which multiple tasks may share data.

        The livetime of this data is the same as the lifetime of the
        Environment.
        @type  name string
        @param name An arbitrary attribute name.
        @type  value object
        @param value Anything.
        """
        assert name is not None
        self.__attributes[name] = value


    def get_attribute(self, name):
        """
        Returns an attribute that was previously defined using
        set_attribute().
        @type  name string
        @param name An arbitrary attribute name.
        @return The value of the attribute with the given name.
        """
        assert name is not None
        if not self.__attributes.has_key(name):
            return None
        return self.__attributes[name]


    def start(self):
        """
        Spiff Constructor calls this to notify the environment any time
        the task iteration starts.
        """
        pass


    def end(self):
        """
        Spiff Constructor calls this to notify the environment any time
        the task iteration ends.
        """
        pass


    def start_task(self, path):
        """
        Spiff Constructor calls this to notify the environment any time
        a task starts.
        @type  path array
        @param path The path of the now handled task.
        """
        pass


    def end_task(self, path):
        """
        Spiff Constructor calls this to notify the environment any time
        a task ends.
        @type  path array
        @param path The path of the now handled task.
        """
        pass


    def get_task_path(self):
        """
        Spiff Constructor uses this to determine which task should be handled
        first. This gives an Environment some limited possibility to modify
        the flow of the tasks in the queue.
        @return array
        """
        return [0]


    def render_markup(self, markup):
        """
        This function renders the given markup.
        Returns True if the result is already available (=the method is
        synchronous), False otherwise (=the method is asynchronous).
        If the result is asynchronous, the Task that triggered the method
        needs to defer any further action until the Constructor is
        re-instantiated at a time where the result can be taken.
        
        This is especially important for stateless protocols like in a Web UI,
        where the result of a markup can only be retrieved when the client
        contacts the server for another web page.
        """
        assert False  # Must be implemented!


    def get_interaction_result(self):
        """
        Returns None if no data is available, InteractionResult otherwise.
        """
        assert False  # Must be implemented!
