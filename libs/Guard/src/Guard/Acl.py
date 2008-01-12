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

class Acl(object):
    def __init__(self,
                 actor_id,
                 action,
                 resource_id,
                 permit    = False,
                 inherited = False):
        self.__id          = -1
        self.__actor_id    = int(actor_id)
        self.__action      = action
        self.__resource_id = int(resource_id)
        self.__permit      = bool(permit)
        self.__inherited   = bool(inherited)

    def __str__(self):
        # WARNING: The resulting string MUST ALWAYS uniquely identify ALL
        # permissions that this ACL specifies; removing any field from the
        # string will result in security bugs.
        # For example, do not replace the IDs by strings such as the name,
        # because the name is not unique.
        permit      = self.__permit    and 'Permit' or 'Deny'
        inherit     = self.__inherited and 'inherited' or ''
        actor_id    = self.__actor_id
        action_id   = self.__action.get_id()
        resource_id = self.__resource_id
        return "%s: %s %s %s (%s)" % (permit,
                                      actor_id,
                                      action_id,
                                      resource_id,
                                      inherit)

    def set_id(self, id):
        self.__id = int(id)

    def get_id(self):
        return self.__id

    def set_actor_id(self, actor_id):
        self.__actor_id = int(actor_id)

    def get_actor_id(self):
        return self.__actor_id

    def set_action(self, action):
        self.__action = action

    def get_action(self):
        return self.__action

    def set_resource_id(self, resource_id):
        self.__resource_id = int(resource_id)

    def get_resource_id(self):
        return self.__resource_id

    def set_permit(self, permit):
        self.__permit = bool(permit)

    def get_permit(self):
        return self.__permit

    def set_inherited(self, inherited = True):
        """
        Defines whether the Acl was inherited from a parent actor.
        """
        self.__inherited = bool(inherited)

    def get_inherited(self):
        """
        Returns True if the Acl was inherited from a parent actor.
        """
        return self.__inherited
