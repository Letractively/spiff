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
class Extension:
    def __init__(self, api):
        self.api   = api
        self.guard = api.get_guard()


    def __content_editor(self):
        if self.api.get_form_value('submit') is not None:
            pass #FIXME
        else:
            self.api.render('templates/content_editor.tmpl')


    def __show_user(self, user):
        assert user is not None
        assert not user.is_group()
        guard = self.guard

        # Collect information for the browser.
        parents = guard.get_resource_parents(user)
        
        # Collect permissions.
        search = {'actor': user, 'resource_section_handle': 'users'}
        acls            = guard.get_permission_list(**search)
        acls_view       = []
        acls_edit       = []
        acls_delete     = []
        acls_non_view   = []
        acls_non_edit   = []
        acls_non_delete = []
        for acl in acls:
            handle = acl.get_action().get_handle()
            permit = acl.get_permit()
            if permit and handle == 'view':
                acls_view.append(acl.get_resource_id())
            elif permit and handle == 'edit':
                acls_edit.append(acl.get_resource_id())
            elif permit and handle == 'delete':
                acls_delete.append(acl.get_resource_id())
            elif handle == 'view':
                acls_non_view.append(acl.get_resource_id())
            elif handle == 'edit':
                acls_non_edit.append(acl.get_resource_id())
            elif handle == 'delete':
                acls_non_delete.append(acl.get_resource_id())

        # Collect more permission info.
        viewable      = guard.get_resource_list_from_id_list(acls_view)
        editable      = guard.get_resource_list_from_id_list(acls_edit)
        deletable     = guard.get_resource_list_from_id_list(acls_delete)
        non_viewable  = guard.get_resource_list_from_id_list(acls_non_view)
        non_editable  = guard.get_resource_list_from_id_list(acls_non_edit)
        non_deletable = guard.get_resource_list_from_id_list(acls_non_delete)

        # Render the template.
        self.api.render('templates/user_editor.tmpl',
                        user                 = user,
                        groups               = parents,
                        viewable_actors      = viewable,
                        editable_actors      = editable,
                        deletable_actors     = deletable,
                        non_viewable_actors  = non_viewable,
                        non_editable_actors  = non_editable,
                        non_deletable_actors = non_deletable)


    def __show_group(self, group):
        assert group is not None
        assert group.is_group()
        guard = self.guard

        # Collect information for the browser.
        children = guard.get_resource_children(group)
        users    = []
        groups   = []
        for child in children:
            if child.is_group():
                groups.append(child)
            else:
                users.append(child)

        # Collect permissions.
        search = {'actor': group, 'resource_section_handle': 'users'}
        acls            = guard.get_permission_list(**search)
        acls_view       = []
        acls_edit       = []
        acls_delete     = []
        acls_non_view   = []
        acls_non_edit   = []
        acls_non_delete = []
        for acl in acls:
            handle = acl.get_action().get_handle()
            permit = acl.get_permit()
            if permit and handle == 'view':
                acls_view.append(acl.get_resource_id())
            elif permit and handle == 'edit':
                acls_edit.append(acl.get_resource_id())
            elif permit and handle == 'delete':
                acls_delete.append(acl.get_resource_id())
            elif handle == 'view':
                acls_non_view.append(acl.get_resource_id())
            elif handle == 'edit':
                acls_non_edit.append(acl.get_resource_id())
            elif handle == 'delete':
                acls_non_delete.append(acl.get_resource_id())

        # Collect more permission info.
        viewable      = guard.get_resource_list_from_id_list(acls_view)
        editable      = guard.get_resource_list_from_id_list(acls_edit)
        deletable     = guard.get_resource_list_from_id_list(acls_delete)
        non_viewable  = guard.get_resource_list_from_id_list(acls_non_view)
        non_editable  = guard.get_resource_list_from_id_list(acls_non_edit)
        non_deletable = guard.get_resource_list_from_id_list(acls_non_delete)

        # Render the template.
        self.api.render('templates/group_editor.tmpl',
                        group                = group,
                        users                = users,
                        groups               = groups,
                        viewable_actors      = viewable,
                        editable_actors      = editable,
                        deletable_actors     = deletable,
                        non_viewable_actors  = non_viewable,
                        non_editable_actors  = non_editable,
                        non_deletable_actors = non_deletable)


    def __user_editor(self):
        id = self.api.get_form_value('id')

        # If no id was given, display the root group.
        if id is None:
            group = self.guard.get_resource_from_handle('everybody', 'users')
            self.__show_group(group)
            return

        # Ending up here, we have an id.
        # Fetch the requested user or group info and display it.
        resource = self.guard.get_resource_from_id(id)
        if resource.is_group():
            self.__show_group(resource)
        else:
            self.__show_user(resource)


    def on_render_request(self):
        self.api.emit('render_start')
        self.api.send_headers()

        if self.api.get_form_value('manage_content') is not None:
            self.__content_editor()
        elif self.api.get_form_value('manage_users') is not None:
            self.__user_editor()
        else:
            self.api.render('templates/admin.tmpl')

        self.api.emit('render_end')
