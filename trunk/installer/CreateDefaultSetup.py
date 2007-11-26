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
from Task          import Task
from Task          import CheckList
from Form          import Form
from StockButton   import StockButton
from User          import User
from Group         import Group
from Content       import Content
from UserAction    import UserAction
from ContentAction import ContentAction

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


    def __create_action(self, name, handle, type):
        assert name   is not None
        assert handle is not None
        caption  = "Creating action '%s'" % name
        action   = self.guard.get_action(handle = handle, type = type)
        if not action:
            action = type(name, handle)
            try:
                self.guard.add_action(action)
            except:
                self._add_result(caption, Task.failure)
                self._print_result(self.environment, False)
                return None
        self._add_result(caption, Task.success)
        return action


    def __create_user_action(self, name, handle):
        return self.__create_action(name, handle, UserAction)


    def __create_content_action(self, name, handle):
        return self.__create_action(name, handle, ContentAction)


    def __create_resource(self,
                          parent,
                          name,
                          handle,
                          type,
                          private = False):
        assert name   is not None
        assert handle is not None
        caption  = "Creating resource '%s'" % name
        resource = self.guard.get_resource(handle = handle, type = type)
        if not resource:
            resource = type(name, handle)
            if private:
                resource.set_attribute('private', True)
            try:
                if parent is None:
                    parent_id = None
                else:
                    parent_id = parent.get_id()
                self.guard.add_resource(parent_id, resource)
            except Exception, e:
                print e
                self._add_result(caption, Task.failure)
                self._print_result(self.environment, False)
                return None
        self._add_result(caption, Task.success)
        return resource


    def __create_group(self, parent, name, handle):
        return self.__create_resource(parent, name, handle, Group)


    def __create_user(self, parent, name, handle):
        return self.__create_resource(parent, name, handle, User)


    def __create_content(self, parent, name, handle, private = False):
        return self.__create_resource(parent, name, handle, Content, private)


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

        user_action_admin = self.__create_user_action('Administer User',
                                                      'administer')
        if user_action_admin is None:
            return Task.failure

        user_action_view = self.__create_user_action('View User',
                                                     'view')
        if user_action_view is None:
            return Task.failure

        user_action_edit = self.__create_user_action('Edit User',
                                                     'edit')
        if user_action_edit is None:
            return Task.failure

        user_action_moderate = self.__create_user_action('Moderate User',
                                                         'moderate')
        if user_action_moderate is None:
            return Task.failure

        #########
        # Assign user permissions.
        #########
        self._result_markup += '{subtitle "Assigning user permissions"}'
        caption = 'Denying all permissions for Everybody'
        actions = [user_action_admin,
                   user_action_view,
                   user_action_edit,
                   user_action_moderate]
        try:
            self.guard.deny(group_everybody, actions, group_everybody)
        except:
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        caption = 'Granting all access to Administrators'
        try:
            self.guard.grant(group_admin, actions, group_everybody)
        except:
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        caption = 'Granting view permission to Users'
        actions = [user_action_view]
        try:
            self.guard.grant(group_users, actions, group_everybody)
        except:
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        #########
        # Create content pages.
        #########
        self._result_markup += '{subtitle "Creating content"}'

        content_default = self.__create_content(None, 'Wiki', 'default')
        if content_default is None:
            return Task.failure

        content_admin = self.__create_content(None,
                                              'Admin Center',
                                              'admin',
                                              True)
        if content_admin is None:
            return Task.failure

        content_admin_register = self.__create_content(content_admin,
                                                       'User Registration',
                                                       'admin/register')
        if content_admin_register is None:
            return Task.failure

        content_admin_login = self.__create_content(content_admin,
                                                    'System Login',
                                                    'admin/login')
        if content_admin_login is None:
            return Task.failure

        content_admin_users = self.__create_content(content_admin,
                                                    'User Manager',
                                                    'admin/users',
                                                    True)
        if content_admin_users is None:
            return Task.failure

        content_admin_page = self.__create_content(content_admin,
                                                   'Page Editor',
                                                   'admin/page',
                                                   True)
        if content_admin_page is None:
            return Task.failure

        content_admin_extensions = self.__create_content(content_admin,
                                                         'Extension Manager',
                                                         'admin/extensions',
                                                         True)
        if content_admin_extensions is None:
            return Task.failure

        #########
        # Assign extensions to the content pages.
        #########
        # Assign the wiki page extension to the homepage.
        caption = 'Assign default page to a wiki'
        content_default.set_attribute('extension', 'spiff_core_wiki_page')
        if not self.guard.save_resource(content_default):
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        # Assign an extension to the admin/register page.
        caption = 'Assign user registration extension to a system page'
        content_admin_register.set_attribute('extension', 'spiff_core_register')
        if not self.guard.save_resource(content_admin_register):
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        # Assign an extension to the admin/login page.
        caption = 'Assign login extension to a system page'
        content_admin_login.set_attribute('extension', 'spiff_core_login')
        if not self.guard.save_resource(content_admin_login):
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        # Assign an extension to the admin page.
        caption = 'Assign admin center extension to a system page'
        content_admin.set_attribute('extension', 'spiff_core_admin_center')
        if not self.guard.save_resource(content_admin):
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        # Assign an extension to the admin/users page.
        caption = 'Assign user manager extension to a system page'
        handle  = 'spiff_core_user_manager'
        content_admin_users.set_attribute('extension', handle)
        if not self.guard.save_resource(content_admin_users):
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        # Assign an extension to the admin/page page.
        caption = 'Assign page editor extension to a system page'
        handle  = 'spiff_core_page_editor'
        content_admin_page.set_attribute('extension', handle)
        if not self.guard.save_resource(content_admin_page):
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        # Assign an extension to the admin/extensions page.
        caption = 'Assign extension manager to a system page'
        handle  = 'spiff_core_extension_manager'
        content_admin_extensions.set_attribute('extension', handle)
        if not self.guard.save_resource(content_admin_extensions):
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        #########
        # Create content permissions.
        #########
        self._result_markup += '{subtitle "Creating content permissions"}'

        content_action_view = self.__create_content_action('View Content',
                                                           'view')
        if content_action_view is None:
            return Task.failure

        content_action_create = self.__create_content_action('Create Content',
                                                             'create')
        if content_action_create is None:
            return Task.failure

        content_action_edit = self.__create_content_action('Edit Content',
                                                           'edit')
        if content_action_edit is None:
            return Task.failure

        content_action_edit_page = self.__create_content_action('Edit Page',
                                                                'edit_page')
        if content_action_edit_page is None:
            return Task.failure

        content_action_delete = self.__create_content_action('Delete Content',
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
                   content_action_edit_page,
                   content_action_delete]
        content = [content_default, content_admin]
        try:
            self.guard.grant(group_admin, actions, content)
        except:
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        caption = 'Granting view permissions to users'
        content = [content_default]
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
