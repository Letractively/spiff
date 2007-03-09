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
        parents = self.guard.get_resource_parents(user)
        self.api.render('templates/user_editor.tmpl',
                        user   = user,
                        groups = parents)


    def __show_group(self, group):
        assert group is not None
        assert group.is_group()

        # Collect information for the browser.
        children = self.guard.get_resource_children(group)
        users    = []
        groups   = []
        for child in children:
            if child.is_group():
                groups.append(child)
            else:
                users.append(child)

        # Collect permissions.
        search = {'actor': group, 'resource_section_handle': 'users'}
        acls        = self.guard.get_permission_list(**search)
        acls_view   = []
        acls_edit   = []
        acls_delete = []
        for acl in acls:
            handle = acl.get_action().get_handle()
            if handle == 'view':
                acls_view.append(acl.get_resource_id())
            elif handle == 'edit':
                acls_edit.append(acl.get_resource_id())
            elif handle == 'delete':
                acls_delete.append(acl.get_resource_id())

        # Collect more permission info.
        viewable  = self.guard.get_resource_list_from_id_list(acls_view)
        editable  = self.guard.get_resource_list_from_id_list(acls_edit)
        deletable = self.guard.get_resource_list_from_id_list(acls_delete)

        # Render the template.
        self.api.render('templates/group_editor.tmpl',
                        group            = group,
                        users            = users,
                        groups           = groups,
                        viewable_actors  = viewable,
                        editable_actors  = editable,
                        deletable_actors = deletable)


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
