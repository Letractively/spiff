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
from User        import User
from Group       import Group
from Page        import Page
from UserAction  import UserAction
from PageAction  import PageAction

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


    def __create_page_action(self, name, handle):
        return self.__create_action(name, handle, PageAction)


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


    def __create_page(self, parent, name, handle, private = False):
        return self.__create_resource(parent, name, handle, Page, private)


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
        # Create pages.
        #########
        self._result_markup += '{subtitle "Creating page"}'

        page_default = self.__create_page(None, 'Wiki', 'default')
        if page_default is None:
            return Task.failure

        page_admin = self.__create_page(None,
                                        'Admin Center',
                                        'admin',
                                        True)
        if page_admin is None:
            return Task.failure

        page_admin_register = self.__create_page(page_admin,
                                                 'User Registration',
                                                 'admin/register')
        if page_admin_register is None:
            return Task.failure

        page_admin_login = self.__create_page(page_admin,
                                              'System Login',
                                              'admin/login')
        if page_admin_login is None:
            return Task.failure

        page_admin_users = self.__create_page(page_admin,
                                              'User Manager',
                                              'admin/users',
                                              True)
        if page_admin_users is None:
            return Task.failure

        page_admin_page = self.__create_page(page_admin,
                                             'Page Editor',
                                             'admin/page',
                                             True)
        if page_admin_page is None:
            return Task.failure

        page_admin_extensions = self.__create_page(page_admin,
                                                   'Extension Manager',
                                                   'admin/extensions',
                                                   True)
        if page_admin_extensions is None:
            return Task.failure

        #########
        # Assign extensions to the pages.
        #########
        # Assign the wiki page extension to the homepage.
        caption = 'Assign default page to a wiki'
        page_default.set_attribute('extension', 'spiff_core_wiki_page')
        page_default.set_attribute('recursive', True)
        if not self.guard.save_resource(page_default):
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        # Assign an extension to the admin/register page.
        caption = 'Assign user registration extension to a system page'
        page_admin_register.set_attribute('extension', 'spiff_core_register')
        if not self.guard.save_resource(page_admin_register):
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        # Assign an extension to the admin/login page.
        caption = 'Assign login extension to a system page'
        page_admin_login.set_attribute('extension', 'spiff_core_login')
        if not self.guard.save_resource(page_admin_login):
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        # Assign an extension to the admin page.
        caption = 'Assign admin center extension to a system page'
        page_admin.set_attribute('extension', 'spiff_core_admin_center')
        page_admin.set_attribute('recursive', True)
        if not self.guard.save_resource(page_admin):
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        # Assign an extension to the admin/users page.
        caption = 'Assign user manager extension to a system page'
        handle  = 'spiff_core_user_manager'
        page_admin_users.set_attribute('extension', handle)
        page_admin_users.set_attribute('recursive', True)
        if not self.guard.save_resource(page_admin_users):
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        # Assign an extension to the admin/page page.
        caption = 'Assign page editor extension to a system page'
        handle  = 'spiff_core_page_editor'
        page_admin_page.set_attribute('extension', handle)
        if not self.guard.save_resource(page_admin_page):
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        # Assign an extension to the admin/extensions page.
        caption = 'Assign extension manager to a system page'
        handle  = 'spiff_core_extension_manager'
        page_admin_extensions.set_attribute('extension', handle)
        if not self.guard.save_resource(page_admin_extensions):
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        #########
        # Create page permissions.
        #########
        self._result_markup += '{subtitle "Creating page permissions"}'

        page_action_view = self.__create_page_action('View Page',
                                                     'view')
        if page_action_view is None:
            return Task.failure

        page_action_create = self.__create_page_action('Create Page',
                                                       'create')
        if page_action_create is None:
            return Task.failure

        page_action_edit = self.__create_page_action('Edit Page',
                                                     'edit')
        if page_action_edit is None:
            return Task.failure

        page_action_edit_content = self.__create_page_action('Edit Page Content',
                                                             'edit_content')
        if page_action_edit_content is None:
            return Task.failure

        page_action_delete = self.__create_page_action('Delete Page',
                                                       'delete')
        if page_action_delete is None:
            return Task.failure

        #########
        # Assign page permissions.
        #########
        self._result_markup += '{subtitle "Assigning page permissions"}'
        caption = 'Granting all permissions to administrators'
        actions = [page_action_create,
                   page_action_view,
                   page_action_edit,
                   page_action_edit_content,
                   page_action_delete]
        page = [page_default, page_admin]
        try:
            self.guard.grant(group_admin, actions, page)
        except:
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        caption = 'Granting view permissions to users'
        page = [page_default]
        try:
            self.guard.grant(group_users, page_action_view, page)
        except:
            self._add_result(caption, Task.failure)
            self._print_result(environment, False)
            return Task.failure
        self._add_result(caption, Task.success)

        self._print_result(environment, result == Task.success)
        return Task.interact

    
    def uninstall(self, environment):
        return Task.success
