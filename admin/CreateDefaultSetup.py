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
from Task        import Task
from Task        import CheckList
from Form        import Form
from StockButton import StockButton
from Guard       import *

class CreateDefaultSetup(CheckList):
    def _print_result(self, environment, done, allow_retry = True):
        if done:
            markup = '{variable check_done "True"}'
            markup += self._result_markup
            form = Form(markup, [StockButton('next_button')])
        elif allow_retry:
            form = Form(self._result_markup, [StockButton('retry_button')])
        else:
            form = Form(self._result_markup, [])
        environment.render_markup(form)


    def __create_resource_section(self, name, handle):
        assert name    is not None
        assert handle  is not None
        caption = "Creating resource section '%s'" % name
        try:
            section = self.guard.get_resource_section_from_handle(handle)
            if section is None:
                section = ResourceSection(name, handle)
                self.guard.add_resource_section(section)
        except:
            self._add_result(caption, Task.failure)
            self._print_result(self.environment, False)
            return None
        self._add_result(caption, Task.success)
        return section


    def __create_action_section(self, name, handle):
        assert name    is not None
        assert handle  is not None
        caption = "Creating action section '%s'" % name
        try:
            section = self.guard.get_action_section_from_handle(handle)
            if section is None:
                section = ActionSection(name, handle)
                self.guard.add_action_section(section)
        except:
            self._add_result(caption, Task.failure)
            self._print_result(self.environment, False)
            return None
        self._add_result(caption, Task.success)
        return section


    def __create_action(self, name, handle, section):
        assert name    is not None
        assert handle  is not None
        assert section is not None
        caption  = "Creating action '%s'" % name
        s_handle = section.get_handle()
        action   = self.guard.get_action_from_handle(handle, s_handle)
        if not action:
            action = Action(name, handle)
            try:
                self.guard.add_action(action, section)
            except:
                self._add_result(caption, Task.failure)
                self._print_result(self.environment, False)
                return None
        self._add_result(caption, Task.success)
        return action


    def __create_user_action(self, name, handle):
        section = ActionSection('user_permissions')
        return self.__create_action(name, handle, section)


    def __create_content_action(self, name, handle):
        section = ActionSection('content_permissions')
        return self.__create_action(name, handle, section)


    def __create_resource(self, group, parent, name, handle, section):
        assert name    is not None
        assert handle  is not None
        assert section is not None
        caption  = "Creating resource '%s'" % name
        s_handle = section.get_handle()
        resource = self.guard.get_resource_from_handle(handle, s_handle)
        if not resource:
            if group:
                resource = ResourceGroup(name, handle)
            else:
                resource = Resource(name, handle)
            try:
                if parent is None:
                    parent_id = None
                else:
                    parent_id = parent.get_id()
                self.guard.add_resource(parent_id, resource, section)
            except:
                self._add_result(caption, Task.failure)
                self._print_result(self.environment, False)
                return None
        self._add_result(caption, Task.success)
        return resource


    def __create_group(self, parent, name, handle):
        section = ResourceSection('users')
        return self.__create_resource(True, parent, name, handle, section)


    def __create_user(self, parent, name, handle):
        section = ResourceSection('users')
        return self.__create_resource(False, parent, name, handle, section)


    def __create_content(self, parent, name, handle):
        section = ResourceSection('content')
        return self.__create_resource(True, parent, name, handle, section)


    def install(self, environment):
        # See if we are done first.
        result = environment.get_interaction_result()
        if result is not None and result.get('check_done') is not None:
            return Task.success

        # Execute child tasks.
        self._result_markup += '{subtitle "Installing required components"}'
        result = Task.success
        for task in self._child_task:
            result = task.install(environment)
            self._add_result(task.get_name(), result)
            if result is not Task.success:
                self._print_result(environment, False)
                return result

        # Now, create our default setup.
        self.environment = environment
        self.guard       = environment.get_attribute('guard_db')

        #########
        # Create users and groups.
        #########
        self._result_markup += '{subtitle "Creating users and groups"}'
        section_users = self.__create_resource_section('Users', 'users')
        if section_users is None:
            return Task.failure

        group_everybody = self.__create_group(None, 'Everybody', 'everybody')
        if group_everybody is None:
            return Task.failure

        group_admin = self.__create_group(group_everybody,
                                          'Administrators',
                                          'administrators')
        if group_admin is None:
            return Task.failure

        user_admin = self.__create_user(group_admin, 'Administrator', 'admin')
        if user_admin is None:
            return Task.failure

        group_users = self.__create_group(group_everybody, 'Users', 'users')
        if group_users is None:
            return Task.failure

        user_anonymous = self.__create_user(group_users,
                                            'Anonymous George',
                                            'anonymous')
        if user_anonymous is None:
            return Task.failure

        #########
        # Create user permissions.
        #########
        self._result_markup += '{subtitle "Creating user permissions"}'
        user_perms = self.__create_action_section('User Permissions',
                                                  'user_permissions')
        if user_perms is None:
            return Task.failure

        user_action_admin = self.__create_user_action('Administer User',
                                                      'administer')
        if user_action_admin is None:
            return Task.failure

        user_action_view = self.__create_user_action('View User',
                                                     'view')
        if user_action_view is None:
            return Task.failure

        user_action_create = self.__create_user_action('Create User',
                                                       'create')
        if user_action_create is None:
            return Task.failure

        user_action_edit = self.__create_user_action('Edit User',
                                                     'edit')
        if user_action_edit is None:
            return Task.failure

        user_action_delete = self.__create_user_action('Delete User',
                                                       'delete')
        if user_action_delete is None:
            return Task.failure

        #########
        # Assign user permissions.
        #########
        self._result_markup += '{subtitle "Assigning user permissions"}'
        caption = 'Granting all access to Administrators'
        actions = [user_action_admin,
                   user_action_view,
                   user_action_create,
                   user_action_edit,
                   user_action_delete]
        try:
            self.guard.grant(group_admin, actions, group_everybody)
        except:
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        #########
        # Create content.
        #########
        self._result_markup += '{subtitle "Creating content"}'
        section_content = self.__create_resource_section('Content', 'content')
        if section_content is None:
            return Task.failure

        content_homepage = self.__create_content(None, 'Homepage', 'homepage')
        if content_homepage is None:
            return Task.failure

        content_system = self.__create_content(None, 'System Pages', 'system')
        if content_system is None:
            return Task.failure

        content_system_login = self.__create_content(content_system,
                                                     'System Login',
                                                     'system/login')
        if content_system_login is None:
            return Task.failure

        # Assign an extension to the system/login page.
        caption = 'Assign login extension to a system page'
        content_system_login.set_attribute('extension', 'spiff_core_login')
        if not self.guard.save_resource(content_system_login, section_content):
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)


        content_system_admin = self.__create_content(content_system,
                                                     'Admin Center',
                                                     'system/admin')
        if content_system_admin is None:
            return Task.failure

        # Assign an extension to the system/admin page.
        caption = 'Assign login extension to a system page'
        content_system_admin.set_attribute('extension', 'spiff_core_admin')
        if not self.guard.save_resource(content_system_admin, section_content):
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        #########
        # Create content permissions.
        #########
        self._result_markup += '{subtitle "Creating content permissions"}'
        content_perms = self.__create_action_section('Content Permissions',
                                                     'content_permissions')
        if content_perms is None:
            return Task.failure

        content_action_view = self.__create_user_action('View Content',
                                                        'view')
        if content_action_view is None:
            return Task.failure

        content_action_create = self.__create_user_action('Create Content',
                                                         'create')
        if content_action_create is None:
            return Task.failure

        content_action_edit = self.__create_user_action('Edit Content',
                                                        'edit')
        if content_action_edit is None:
            return Task.failure

        content_action_delete = self.__create_user_action('Delete Content',
                                                          'delete')
        if content_action_delete is None:
            return Task.failure

        #########
        # Assign content permissions.
        #########
        self._result_markup += '{subtitle "Assigning content permissions"}'
        caption = 'Granting all permissions to administrators'
        actions = [content_action_create,
                   content_action_view,
                   content_action_edit,
                   content_action_delete]
        content = [content_homepage, content_system]
        try:
            self.guard.grant(group_admin, actions, content)
        except:
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        caption = 'Granting view permissions to users'
        content = [content_homepage, content_system]
        try:
            self.guard.grant(group_users, content_action_view, content)
        except:
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        self._print_result(environment, result == Task.success)
        return Task.interact

    
    def uninstall(self, environment):
        return Task.success
