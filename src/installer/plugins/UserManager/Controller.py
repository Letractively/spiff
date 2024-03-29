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
import gettext
_ = gettext.gettext
import SpiffGuard
from string   import split
from services import ExtensionController
from services import UserDB
from objects  import User
from objects  import Group
from objects  import UserAction

class Controller(ExtensionController):
    def __init__(self, api, api_key):
        ExtensionController.__init__(self, api, api_key)
        self.guard  = api.get_guard()
        self.userdb = UserDB(self.guard)


    def __show_user(self, user, path, errors = []):
        assert user is not None
        assert not user.is_group()
        assert path is not None

        # Make sure that current_user has "view" permissions on it.
        current_user = self.api.get_current_user()
        if user.get_id() is not None:
            view = self.guard.get_action(handle = 'view', type = UserAction)
            assert view is not None
            if not self.guard.has_permission(current_user, view, user):
                user     = User(user.get_name())
                errors   = [_("You do not have permission to view " +
                                 "this user.")]

        # Collect information for the browser.
        if user.get_id() is None:
            parent_id = path.crop().get_current_id()
            parent    = self.guard.get_resource(id = parent_id)
            parent.set_attribute('path_str', path.crop().get())
            parents   = [parent]
            acls      = []
        else:
            acls    = self.userdb.get_permission_list(user)
            parents = self.guard.get_resource_parents(user)
            # Abuse attributes to pass the path to the HTML template.
            for parent in parents:
                ppath = self.guard.get_resource_path_from_id(parent.get_id())
                parent.set_attribute('path_str', ppath.get())
        
        # Render the template.
        self.api.render('user_editor.tmpl',
                        path         = path,
                        user         = user,
                        groups       = parents,
                        acls         = acls,
                        get_resource = self.guard.get_resource,
                        errors       = errors)


    def __show_group(self, group, path, errors = []):
        assert group is not None
        assert group.is_group()
        assert path is not None

        # Make sure that current_user has "view" permissions on it.
        current_user = self.api.get_current_user()
        if group.get_id() is not None:
            view = self.guard.get_action(handle = 'view', type = UserAction)
            assert view is not None
            if not self.guard.has_permission(current_user, view, group):
                group     = Group(group.get_name())
                errors    = [_("You do not have permission to view " +
                                  "this group.")]

        # Collect information for the browser.
        users    = []
        groups   = []
        if group.get_id() is not None:
            acls     = self.userdb.get_permission_list(group)
            parents  = self.guard.get_resource_parents(group)
            children = self.guard.get_resource_children(group)
            for child in children:
                if child.is_group():
                    groups.append(child)
                else:
                    users.append(child)
        else:
            parent_id = path.crop().get_current_id()
            parent    = self.guard.get_resource(id = parent_id)
            parents   = [parent]
            acls      = []

        # Render the template.
        self.api.render('group_editor.tmpl',
                        path         = path,
                        parents      = parents,
                        group        = group,
                        users        = users,
                        groups       = groups,
                        acls         = acls,
                        get_resource = self.guard.get_resource,
                        errors       = errors)


    def __save_resource(self, resource):
        assert resource is not None
        self.guard = self.guard
        
        # Retrieve form data.
        get_data             = self.api.get_data()
        post_data            = self.api.post_data()
        path                 = None
        path_str             = get_data.get_str('path_str')
        name                 = post_data.get_str('name')
        description          = post_data.get_str('description')
        use_group_permission = post_data.get_bool('use_group_permission')
        default_owner_id     = post_data.get_int('default_owner_id')
        resource_list        = post_data.get('resource[]',   [])
        permission_list      = post_data.get('permission[]', [])
        if path_str is not None:
            path = SpiffGuard.ResourcePath(path_str) # FIXME: Take reference from elsewhere.
        if path is not None:
            parent_id = path.get_parent_id()
        if resource.is_group() and parent_id is None:
            parent_id = 0  # Given resource is a top-level group.
        if use_group_permission is not None:
            use_group_permission = int(use_group_permission)
        if default_owner_id is not None:
            default_owner_id = int(default_owner_id)

        # Validate form data.
        errors = []
        parent = None

        # Parent ID must be >= 0.
        if parent_id is None or parent_id < 0:
            msg = _("Invalid parent id.")
            errors.append(msg)

        # A resource can not be its own parent/child.
        elif parent_id == resource.get_id():
            msg = _("A resource can not be its own parent.")
            errors.append(msg)

        # Users and groups must have a parent, except existing ones.
        elif resource.get_id() is None and parent_id == 0:
            msg = _("Can not create a user or group without a parent.")
            errors.append(msg)

        # So a parent was given - make sure that it exists.
        elif parent_id > 0:
            parent = self.guard.get_resource(id = parent_id)
            if parent is None:
                msg = _("Specified parent does not exist.")
                errors.append(msg)

        # Check permissions.
        current_user    = self.api.get_current_user()
        current_user_id = current_user.get_id()

        # If the given user/group is new, make sure that current_user has
        # "administer" permissions on the parent.
        if resource.get_id() is None:
            admin = self.guard.get_action(handle = 'administer',
                                        type   = UserAction)
            assert admin is not None
            if not self.guard.has_permission(current_user, admin, parent):
                return [_("You do not have permission to add a group.")]

        # If the given group already exists, make sure that current_user
        # has "edit" permissions on it.
        elif resource.is_group():
            edit = self.guard.get_action(handle = 'edit', type = UserAction)
            assert edit is not None
            if not self.guard.has_permission(current_user, edit, resource):
                return [_("You do not have permission to edit this group.")]

        # If the given user already exists, make sure that current_user
        # has "edit" permissions on it.
        else:
            edit = self.guard.get_action(handle = 'edit',
                                       type   = UserAction)
            assert edit is not None
            if not self.guard.has_permission(current_user, edit, resource):
                return [_("You do not have permission to edit this user.")]

        # Minimum name length.
        if name is None or len(name) < 2:
            msg = _("The name must be at least two characters long.")
            errors.append(msg)

        # Make sure that the user/group name does not yet exist.
        elif resource.get_id() is None:
            res = self.guard.get_resource(name = name, type = User)
            if res is not None and res.is_group():
                msg = _("A group with the given name already exists.")
                errors.append(msg)
            elif res is not None:
                msg = _("A user with the given name already exists: %s" % res.get_name())
                errors.append(msg)

        # Groups require the use_group_permission field.
        if resource.is_group():
            if use_group_permission not in [0, 1]:
                msg = _("Group has an invalid default owner.")
                errors.append(msg)

        # New users require the default_owner_id field set to either 0 or
        # to the parent_id.
        elif parent is not None and resource.get_id() is None:
            if default_owner_id != 0 and default_owner_id != parent_id:
                msg = _("Specified parent does not exist.")
                errors.append(msg)

        # Existing users require the default_owner_id field set to either 0
        # or one of the parent ids.
        elif parent is not None and default_owner_id != 0:
            parents = self.guard.get_resource_parents(resource)
            found   = False
            if parents is not None:
                for parent in parents:
                    if int(default_owner_id) == parent.get_id():
                        found = True
                        break
            if not found:
                msg = _("User has an invalid default owner.")
                errors.append(msg)

        # Make sure that the user/group names for which permissions were
        # defined exist in the database.
        have_already = {}
        for rname in resource_list:
            res = self.guard.get_resource(name = rname, type = User)
            if res is not None:
                continue
            msg = _("User or group '%s' does not exists." % rname)
            errors.append(msg)

            # Make sure that a user does not have two sets of permissions
            # defined.
            if not have_already.has_key(rname):
                have_already[rname] = True
                continue

            if res.is_group():
                msg = _("Permission for group '%s' was specified twice."
                           % rname)
            else:
                msg = _("Permission for user '%s' was specified twice."
                           % rname)
            errors.append(msg)

        # Bail out if an error occured.
        if len(errors) > 0:
            return errors

        # Cool, everything looks clean! Store the data in the resource and
        # save it.
        resource.set_name(name)
        resource.set_attribute('description', description)
        if resource.is_group():
            resource.set_attribute('use_group_permission',
                                   use_group_permission)
        else:
            resource.set_attribute('default_owner_id', default_owner_id)
        if resource.get_id() is None:
            self.guard.add_resource(parent_id, resource)
        else:
            self.guard.save_resource(resource)

        #i = 0
        #for item in resource_list:
        #    print "RESOURCES:", item
        #    print "PERMS:", permission_list[i]
        #    i += 1

        # Get the list of current permissions from the database.
        search = { 'resource_type': User }
        acls   = self.guard.get_permission_list_from_id(resource.get_id(),
                                                      **search)

        resource_id_list = []
        for acl in acls:
            acl_id      = acl.get_id()
            actor_id    = acl.get_actor_id()
            action      = acl.get_action()
            action_id   = action.get_id()
            resource_id = acl.get_resource_id()
            res         = self.guard.get_resource(id = resource_id)
            resource_id_list.append(resource_id)
            cur_permit  = self.guard.has_permission_from_id(current_user_id,
                                                            action_id,
                                                            resource_id)

            # If the resource was removed from the UI, delete it from the DB.
            if res.get_name() not in resource_list:
                #print "Missing resource: Deleting permission %s" % acl_id
                # If deleting this permission would escalate the permission
                # of that user to something that is higher than current_user,
                # deny that.
                par_permit = self.guard.has_permission_from_id(parent_id,
                                                               action_id,
                                                               resource_id)
                if par_permit and not cur_permit:
                    return [_("Permission change would escalate rights " +
                                 "above the currently logged in user.")]
                assert self.guard.delete_permission_from_id(actor_id,
                                                            action.get_id(),
                                                            resource_id)
                continue

            # Get the permissions that were defined for the resource.
            resource_permission = None
            seq                 = 0
            for rname in resource_list:
                if rname == res.get_name():
                    resource_permission = split(permission_list[seq], '/')
                seq += 1
            assert resource_permission is not None

            # If the specific permission was removed from the UI, also remove
            # it from the DB.
            if action.get_handle() not in resource_permission:
                #print "Missing permission: Deleting permission %s" % acl_id
                # If deleting this permission would escalate the permission
                # of that user to something that is higher than current_user,
                # deny that.
                par_permit = self.guard.has_permission_from_id(parent_id,
                                                               action_id,
                                                               resource_id)
                if par_permit and not cur_permit:
                    return [_("Permission change would escalate rights " +
                                 "above the currently logged in user.")]
                assert self.guard.delete_permission_from_id(actor_id,
                                                            action.get_id(),
                                                            resource_id)
                continue

        # Walk through all permissions that were defined in the UI and make
        # sure that they exist in the database.
        seq      = 0
        view     = self.guard.get_action(handle = 'view',     type = UserAction)
        edit     = self.guard.get_action(handle = 'edit',     type = UserAction)
        moderate = self.guard.get_action(handle = 'moderate', type = UserAction)
        for name in resource_list:
            resource_permission = split(permission_list[seq], '/')
            seq += 1
            if 'default' in resource_permission:
                continue

            res = self.guard.get_resource(name = name, type = User)
            #print "Current:", resource.get_name(), res.get_name(), resource_permission

            # Walk through all permissions, granting all that were newly added.
            for permission in resource_permission:
                if permission == 'none':
                    continue
                #print "Granting %s on %s" % permission, res.get_name())
                action_id  = locals()[permission].get_id()
                cur_permit = self.guard.has_permission_from_id(current_user_id,
                                                               action_id,
                                                               resource_id)
                if not self.guard.has_permission_from_id(current_user_id,
                                                         action_id,
                                                         resource_id):
                    return [_("Permission change would escalate rights " +
                                 "above the currently logged in user.")]
                assert self.guard.grant_from_id(resource.get_id(),
                                                action_id,
                                                res.get_id())

            # Walk through all permissions, denying all that were listed as
            # rejected.
            for permission in ['view', 'edit', 'moderate']:
                if permission in resource_permission:
                    continue
                #print "Denying %s on %s" % permission, res.get_name())
                action_id = locals()[permission].get_id()
                assert self.guard.deny_from_id(resource.get_id(),
                                               action_id,
                                               res.get_id())

        return None


    def __delete_resource(self, resource):
        assert resource is not None

        # Check permissions.
        current_user = self.api.get_current_user()

        # Make sure that current_user has "edit" permissions on it.
        edit = self.guard.get_action(handle = 'edit', type = UserAction)
        assert edit is not None
        permit = self.guard.has_permission(current_user, edit, resource)
        if not permit and resource.is_group():
            return [_("You do not have permission to delete this group.")]
        elif not permit:
            return [_("You do not have permission to delete this user.")]

        assert self.guard.delete_resource(resource) > 0
        return None


    def index(self, **kwargs):
        # Find out which item was requested.
        path_str = self.api.get_data().get_str('path_str')
        if path_str is None:
            resource = self.guard.get_resource(handle = 'everybody',
                                               type   = Group)
            path = SpiffGuard.ResourcePath([resource.get_id()])
        else:
            path = SpiffGuard.ResourcePath(path_str)

        # Fetch the requested user or group info.
        errors = []
        id     = path.get_current_id()
        if self.api.post_data().get_bool('group_add'):
            resource = Group('')
            path     = path.append(0)
        elif self.api.post_data().get_bool('user_add'):
            resource = User('')
            path     = path.append(0)
        elif self.api.post_data().get_bool('group_save') and id == 0:
            resource = Group('')
            errors   = self.__save_resource(resource)
            if not errors:
                path = path.crop().append(resource.get_id())
        elif self.api.post_data().get_bool('group_save'):
            resource = self.guard.get_resource(id = id)
            errors   = self.__save_resource(resource)
            path     = path.crop().append(resource.get_id())
        elif self.api.post_data().get_bool('user_save') and id == 0:
            resource = User('')
            errors   = self.__save_resource(resource)
            if not errors:
                path = path.crop().append(resource.get_id())
        elif self.api.post_data().get_bool('user_save'):
            resource = self.guard.get_resource(id = id)
            errors   = self.__save_resource(resource)
            path     = path.crop().append(resource.get_id())
        elif (self.api.post_data().get_bool('group_delete') and
              self.api.post_data().get_str('group_delete_really') == 'yes'):
            resource = self.guard.get_resource(id = id)
            # Check if the group still has users in it.
            children = self.guard.get_resource_children(resource)
            if len(children) > 0:
                #FIXME: Rather ask what to do with the children.
                errors = [_("Group can not be deleted because " +
                                    "it still has users in it.")]
            else:
                errors   = self.__delete_resource(resource)
                path     = path.crop()
                id       = path.get_current_id()
                resource = self.guard.get_resource(id = id)
        elif (self.api.post_data().get_bool('user_delete') and
              self.api.post_data().get_str('user_delete_really') == 'yes'):
            resource = self.guard.get_resource(id = id)
            errors   = self.__delete_resource(resource)
            path     = path.crop()
            id       = path.get_current_id()
            resource = self.guard.get_resource(id = id)
        elif path_str is not None:
            resource = self.guard.get_resource(id = id)

        # Display the editor.
        if resource.is_group():
            self.__show_group(resource, path, errors)
        else:
            self.__show_user(resource, path, errors)
