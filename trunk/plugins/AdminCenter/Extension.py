"""
extension:    Admin Center
handle:       spiff_core_admin_center
version:      0.1
author:       Samuel Abels
author-email: spam2@debain.org
description:  This core extension implements the admininistration user interface.
dependency:   spiff spiff_core_login
signal:       render_start
              render_end
"""
from string import split

class Extension:
    def __init__(self, api):
        self.api      = api
        self.i18n     = api.get_i18n()
        self.guard    = api.get_guard()
        self.guard_db = api.get_guard_db()


    def __content_editor(self):
        if self.api.get_form_value('submit') is not None:
            pass #FIXME
        else:
            self.api.render('templates/content_editor.tmpl')


    def __parse_permissions(self, permission_str):
        permissions = []
        for permission in split(permission_str, ','):
            permission = permission.strip()
            if permission == '':
                continue
            if len(permission) < 2:
                return None
            permissions.append(permission)
        return permissions


    def __get_permissions_from_db(self, resource):
        guard_db = self.guard_db

        # Retrieve a list of all ACLs.
        search = {'actor': resource, 'resource_section_handle': 'users'}
        acls   = guard_db.get_permission_list_with_inheritance(**search)

        # Sort them into a dict, mapping resource_id to ACL.
        acls_dict = {}
        for acl in acls:
            acl_actions = acls_dict.get(acl.get_resource_id(), [])
            acl_actions.append(acl)
            acls_dict[acl.get_resource_id()] = acl_actions

        # Retrieve additional info about the resource.
        acl_id_list   = acls_dict.keys()
        resource_list = guard_db.get_resource_list_from_id_list(acl_id_list)

        # Map resource to acl.
        acls = {}
        for resource in resource_list:
            acls[resource] = acls_dict[resource.get_id()]

        # Dump
        #for resource in acls:
        #    acl_list = acls[resource]
        #    print "Resource:", resource.get_name()
        #    for acl in acl_list:
        #        print "ACL:", acl.get_action().get_name(), acl.get_permit(), acl.get_inherited()
        
        return acls


    def __show_user(self, user, path, errors = []):
        assert user is not None
        assert not user.is_group()
        assert path is not None
        guard_db = self.guard_db

        # Collect information for the browser.
        if user.get_id() > 0:
            parents = guard_db.get_resource_parents(user)
            # Abuse attributes to pass the path to the HTML template.
            for parent in parents:
                ppath = guard_db.get_resource_path_from_id(parent.get_id())
                parent.set_attribute('path_str', ppath.get())
        else:
            parent_id = path.crop().get_current_id()
            parent    = guard_db.get_resource_from_id(parent_id)
            parent.set_attribute('path_str', path.crop().get())
            parents   = [parent]
        
        # Collect permissions.
        acls = self.__get_permissions_from_db(user)

        # Render the template.
        self.api.render('templates/user_editor.tmpl',
                        path                 = path,
                        user                 = user,
                        groups               = parents,
                        acls                 = acls,
                        errors               = errors)


    def __show_group(self, group, path, errors = []):
        assert group is not None
        assert group.is_group()
        assert path is not None
        guard_db = self.guard_db

        # Collect information for the browser.
        if group.get_id() > 0:
            parents = guard_db.get_resource_parents(group)
        else:
            parent_id = path.crop().get_current_id()
            parent    = guard_db.get_resource_from_id(parent_id)
            parents   = [parent]
        children = guard_db.get_resource_children(group)
        users    = []
        groups   = []
        for child in children:
            if child.is_group():
                groups.append(child)
            else:
                users.append(child)

        # Collect permissions.
        acls = self.__get_permissions_from_db(group)

        # Render the template.
        self.api.render('templates/group_editor.tmpl',
                        path                 = path,
                        parents              = parents,
                        group                = group,
                        users                = users,
                        groups               = groups,
                        acls                 = acls,
                        errors               = errors)


    def __save_resource(self, resource):
        assert resource is not None
        
        # Retrieve form data.
        get_data             = self.api.get_get_data
        post_data            = self.api.get_post_data
        path                 = None
        path_str             = get_data('path_str')
        name                 = post_data('name')
        description          = post_data('description')
        use_group_permission = post_data('use_group_permission')
        default_owner_id     = post_data('default_owner_id')
        viewable_actors      = post_data('viewable_actors')
        editable_actors      = post_data('editable_actors')
        deletable_actors     = post_data('deletable_actors')
        non_viewable_actors  = post_data('non_viewable_actors')
        non_editable_actors  = post_data('non_editable_actors')
        non_deletable_actors = post_data('non_deletable_actors')
        if path_str is not None:
            path = self.guard.ResourcePath(path_str)
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
            msg = self.i18n("Invalid parent id.")
            errors.append(msg)

        # A resource can not be its own parent/child.
        elif parent_id == resource.get_id():
            msg = self.i18n("A resource can not be its own parent.")
            errors.append(msg)

        # Users *have to* have a parent (unlike groups, whose parent may be
        # 0).
        elif parent_id == 0 and not resource.is_group():
            msg = self.i18n("Can not create a user without a group.")
            errors.append(msg)

        # So a parent was given - make sure that it exists.
        elif parent_id > 0:
            parent = self.guard_db.get_resource_from_id(parent_id)
            if parent is None:
                msg = self.i18n("Specified parent does not exist.")
                errors.append(msg)

        # Minimum name length.
        if name is None or len(name) < 2:
            msg = self.i18n("The name must be at least two characters long.")
            errors.append(msg)

        # Groups require the use_group_permission field.
        if resource.is_group():
            if use_group_permission not in [0, 1]:
                msg = self.i18n("Group has an invalid default owner.")
                errors.append(msg)

        # New users require the default_owner_id field set to either 0 or
        # to the parent_id.
        elif parent is not None and resource.get_id() <= 0:
            if default_owner_id != 0 and default_owner_id != parent_id:
                msg = self.i18n("Specified parent does not exist.")
                errors.append(msg)

        # Existing users require the default_owner_id field set to either 0
        # or one of the parent ids.
        elif parent is not None and default_owner_id != 0:
            parents = self.guard_db.get_resource_parents(resource)
            found   = False
            if parents is not None:
                for parent in parents:
                    if int(default_owner_id) == parent.get_id():
                        found = True
                        break
            if not found:
                msg = self.i18n("User has an invalid default owner.")
                errors.append(msg)

        # Check the syntax of the permission fields.
        permission_fields = {
          'viewable_actors':      self.i18n('Viewable Users'),
          'editable_actors':      self.i18n('Editable Users'),
          'deletable_actors':     self.i18n('Deletable Users'),
          'non_viewable_actors':  self.i18n('Non-Viewable Users'),
          'non_editable_actors':  self.i18n('Non-Editable Users'),
          'non_deletable_actors': self.i18n('Non-Deletable Users'),
        }
        for field in permission_fields:
            if locals()[field] is None:
                continue
            # Syntax check.
            list = self.__parse_permissions(locals()[field])
            if list is None:
                fname = permission_fields[field]
                msg   = self.i18n("'%s' field has invalid content." % fname)
                errors.append(msg)
                continue

            # Make sure that the specified users/groups exist.
            for rname in list:
                res = self.guard_db.get_resource_from_name(rname, 'users')
                if res is not None:
                    continue
                msg = self.i18n("User or group '%s' does not exists." % rname)
                errors.append(msg)

        #FIXME: Make sure that "grant" permission for a user is not requested
        # at the same time as "deny" permission.

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
        section = self.guard_db.get_resource_section_from_handle('users')
        if resource.get_id() <= 0:
            self.guard_db.add_resource(parent_id, resource, section)
        else:
            self.guard_db.save_resource(resource, section)

        # Get the list of permissions from the database.
        (viewable,
         editable,
         deletable,
         non_viewable,
         non_editable,
         non_deletable) = self.__get_permissions_from_db(resource)

        # Save changed permissions.
        permission_fields = {
          'viewable_actors':      'view',
          'editable_actors':      'edit',
          'deletable_actors':     'delete',
          'non_viewable_actors':  'view',
          'non_editable_actors':  'edit',
          'non_deletable_actors': 'delete',
        }
        for field in permission_fields:
            # Extract fields.
            if locals()[field] is None:
                list = []
            else:
                list = self.__parse_permissions(locals()[field])

            # Retrieve the action.
            section   = 'user_permissions'
            handle    = permission_fields[field]
            action    = self.guard_db.get_action_from_handle(handle, section)
            actor_id  = resource.get_id()
            action_id = action.get_id()
            permit    = not field.startswith('non_')
            assert action is not None

            # Delete all permissions that are no longer specified.
            old_field = field[:-7] # Strip "_actors" from the field name.
            for group in locals()[old_field]:
                if group.get_name() not in list:
                    #print "DELETE:", group.get_name(), field
                    resource_id = group.get_id()
                    assert self.guard_db.delete_permission_from_id(actor_id,
                                                                   action_id,
                                                                   resource_id)

            # Create all new permissions.
            for group_name in list:
                found = False
                for group in locals()[old_field]:
                    if group.get_name() == group_name:
                        found = True
                        break
                if not found:
                    #print "ADD:", group_name, field
                    res = self.guard_db.get_resource_from_name(group_name,
                                                               'users')
                    assert res is not None
                    resource_id = res.get_id()
                    assert self.guard_db.set_permission_from_id(actor_id,
                                                                action_id,
                                                                resource_id,
                                                                permit)

        return None


    def __user_editor(self):
        path_str = self.api.get_get_data('path_str')

        # Find out which item was requested.
        if path_str is None:
            resource = self.guard_db.get_resource_from_handle('everybody',
                                                              'users')
            path     = self.guard.ResourcePath([resource.get_id()])
        else:
            path = self.guard.ResourcePath(path_str)

        # Fetch the requested user or group info.
        errors = []
        id     = int(path.get_current_id())
        if self.api.get_post_data('group_add') is not None:
            resource = self.guard.ResourceGroup('')
            path     = path.append(0)
        elif self.api.get_post_data('user_add') is not None:
            resource = self.guard.Resource('')
            path     = path.append(0)
        elif self.api.get_post_data('group_save') is not None and id == 0:
            resource = self.guard.ResourceGroup('')
            errors   = self.__save_resource(resource)
            path     = path.crop().append(resource.get_id())
        elif self.api.get_post_data('group_save') is not None:
            resource = self.guard_db.get_resource_from_id(id)
            errors   = self.__save_resource(resource)
            path     = path.crop().append(resource.get_id())
        elif self.api.get_post_data('user_save') is not None and id == 0:
            resource = self.guard.Resource('')
            errors   = self.__save_resource(resource)
            path     = path.crop().append(resource.get_id())
        elif self.api.get_post_data('user_save') is not None:
            resource = self.guard_db.get_resource_from_id(id)
            errors   = self.__save_resource(resource)
            path     = path.crop().append(resource.get_id())
        elif path_str is not None:
            resource = self.guard_db.get_resource_from_id(id)

        # Display the editor.
        if resource.is_group():
            self.__show_group(resource, path, errors)
        else:
            self.__show_user(resource, path, errors)


    def on_render_request(self):
        self.api.emit('render_start')
        self.api.send_headers()

        if self.api.get_get_data('manage_content') is not None:
            self.__content_editor()
        elif self.api.get_get_data('manage_users') is not None:
            self.__user_editor()
        else:
            self.api.render('templates/admin.tmpl')

        self.api.emit('render_end')
