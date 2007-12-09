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
from User       import User
from Group      import Group
from UserAction import UserAction

class UserDB(object):
    def __init__(self, guard):
        self.__guard = guard
        guard.register_type([User, Group, UserAction])
        

    def get_user(self, handle):
        return self.__guard.get_resource(handle = handle, type = User)


    def add_user(self, parent, user):
        return self.__guard.add_resource(parent, user)


    def save_user(self, user):
        return self.__guard.save_resource(user)


    def delete_user(self, user):
        return self.__guard.delete_resource(user)


    def get_group(self, handle):
        return self.__guard.get_resource(handle = handle, type = Group)


    def add_group(self, parent, group):
        return self.__guard.add_resource(parent, group)


    def save_group(self, group):
        return self.__guard.save_resource(group)


    def delete_group(self, group):
        return self.__guard.delete_resource(group)


    def get_permission_list(self, resource):
        # Retrieve a list of all ACLs. The result is ordered by actor_path,
        # resource_path.
        search = {'actor':         resource,
                  'actor_type':    [User, Group],
                  'resource_type': [User, Group]}
        acls   = self.__guard.get_permission_list_with_inheritance(**search)

        # Retrieve additional info about the resource.
        res_id_list = [acl.get_resource_id() for acl in acls]
        res_list    = self.__guard.get_resources(id = res_id_list)
        res_dict    = dict([(r.get_id(), r) for r in res_list])

        # Group them by resource into a list that contains (resource,
        # [acl1, acl2, ...]) tuples.
        resource_acls = []
        last_resource = None
        for acl in acls:
            resource = res_dict[acl.get_resource_id()]
            if last_resource == resource:
                resource_acls[-1][1].append(acl)
            else:
                resource_acls.append((resource, [acl]))
                last_resource = resource

        return resource_acls
