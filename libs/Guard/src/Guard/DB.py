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
from DBReader     import DBReader
from functions    import int2bin
from sqlalchemy   import *
from Resource     import Resource
from ResourcePath import ResourcePath
import string, datetime

class DB(DBReader):
    def install(self):
        """
        Installs (or upgrades) database tables.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        for table in self._table_list:
            table.create(checkfirst = True)
        return True


    def uninstall(self):
        """
        Drops all tables from the database. Use with care.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        for table in self._table_list[::-1]:
            table.drop(checkfirst = True)
        return True


    def clear_database(self):
        """
        Drops the content of any database table used by this library.
        Use with care.

        Wipes out everything, including types, actions, resources and acls.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        delete = self._table_map['resource'].delete()
        result = delete.execute()
        delete = self._table_map['action'].delete()
        result = delete.execute()
        return True


    def __add_action1(self, action):
        """
        Inserts the given action into the database.

        @type  action: Action
        @param action: The action to be added.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        if action is None:
            raise AttributeError('action argument must not be None')
        if action.__class__.__name__ not in self._types:
            raise AttributeError('action type is not yet registered')

        insert = self._table_map['action'].insert()
        result = insert.execute(action_type = action.__class__.__name__,
                                handle      = action.get_handle(),
                                name        = action.get_name())
        action.set_id(result.last_inserted_ids()[0])
        self._action_cache_add(action)
        return True


    def add_action(self, actions):
        """
        Inserts the given action into the database.

        @type  actions: Action|list[Action]
        @param actions: The actions to be added.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        if actions is None:
            raise AttributeError('action argument must not be None')
        if type(actions) != type([]):
            actions = [actions]
        for action in actions:
            self.__add_action1(action)
        return True


    def __save_action1(self, action):
        """
        Updates the given action in the database. Does nothing if the
        action is not yet in the database.

        @type  action: Action
        @param action: The action to be saved.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        if action is None:
            raise AttributeError('action argument must not be None')
        if action.__class__.__name__ not in self._types:
            raise AttributeError('action type is not yet registered')

        table  = self._table_map['action']
        update = table.update(table.c.id == action.get_id())
        result = update.execute(action_type = action.__class__.__name__,
                                handle      = action.get_handle(),
                                name        = action.get_name())
        self._action_cache_flush()
        self._action_cache_add(action)
        return True


    def save_action(self, actions):
        """
        Updates the given actions in the database. Does nothing if
        the action doesn't exist.

        @type  actions: Action|list[Action]
        @param actions: The action to be saved.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        if actions is None:
            raise AttributeError('action argument must not be None')
        if type(actions) != type([]):
            actions = [actions]
        for action in actions:
            self.__save_action1(action)
        return True


    def delete_action(self, actions):
        """
        Convenience wrapper around delete_action_from_match().

        @type  actions: Action|list[Action]
        @param actions: The actions to be removed.
        @rtype:  int
        @return: The number of deleted actions.
        """
        if actions is None:
            raise AttributeError('action argument must not be None')
        if type(actions) != type([]):
            actions = [actions]
        ids = [action.get_id() for action in actions]
        res = self.delete_action_from_match(id = ids)
        for action in actions:
            action.set_id(None)
        return res


    def delete_action_from_match(self, **kwargs):
        """
        Deletes all actions that match the given criteria from the
        database.
        All ACLs associated with the action are removed.

        @type  kwargs: dict
        @param kwargs: The following keys may be used:
                         - id - the id of the resource
                         - handle - the handle of the resource
                         - type - the class type of the resource
                       All values may also be lists (logical OR).
        @rtype:  int
        @return: The number of deleted actions.
        """
        tbl_a = self._table_map['action']
        table = tbl_a
        where = None

        # ID.
        if kwargs.has_key('id'):
            ids = kwargs.get('id')
            if type(ids) == type(0):
                ids = [ids]
            id_where = None
            for id in ids:
                id_where = or_(id_where, table.c.id == id)
            where = and_(where, id_where)

        # Handle.
        if kwargs.has_key('handle'):
            handles = kwargs.get('handle')
            if type(handles) != type([]):
                handles = [handles]
            handle_where = None
            for handle in handles:
                handle_where = or_(handle_where, table.c.handle == handle)
            where = and_(where, handle_where)

        # Object type.
        if kwargs.has_key('type'):
            types = kwargs.get('type')
            cond  = self._get_subtype_sql(tbl_a.c.action_type, types)
            where = and_(where, cond)

        delete = table.delete(where)
        result = delete.execute()

        if result.rowcount > 0:
            self._action_cache_flush()
        return result.rowcount


    def __resource_has_attribute(self, resource_id, name):
        assert resource_id >= 0
        assert name is not None
        table  = self._table_map['resource_attribute']
        select = table.select(and_(table.c.resource_id == resource_id,
                                   table.c.name        == name))
        result = select.execute()
        row    = result.fetchone()
        if row is not None:
            return True
        return False


    def __resource_add_attribute(self, resource_id, name, value):
        assert resource_id >= 0
        assert name is not None
        if self.__resource_has_attribute(resource_id, name):
            self.__resource_update_attribute(resource_id, name, value)
            return None
        insert = self._table_map['resource_attribute'].insert()
        if value is None:
            value = ''
        if type(value) == type(0):
            result = insert.execute(resource_id = resource_id,
                                    name        = name,
                                    type        = self.attrib_type_int,
                                    attr_int    = value)
        elif type(value) == type(True):
            result = insert.execute(resource_id = resource_id,
                                    name        = name,
                                    type        = self.attrib_type_bool,
                                    attr_int    = int(value))
            
        elif type(value) == type(''):
            result = insert.execute(resource_id = resource_id,
                                    name        = name,
                                    type        = self.attrib_type_string,
                                    attr_string = value)
        else:
            raise Exception('Unknown attribute type %s' % type(value))
        return result.last_inserted_ids()[0]


    def __resource_update_attribute(self, resource_id, name, value):
        assert resource_id >= 0
        assert name is not None
        table  = self._table_map['resource_attribute']
        update = table.update(and_(table.c.resource_id == resource_id,
                                   table.c.name        == name))
        if value is None:
            value = ''
        if type(value) == type(0):
            result = update.execute(type        = self.attrib_type_int,
                                    name        = name,
                                    attr_int    = value)
        elif type(value) == type(True):
            result = update.execute(type        = self.attrib_type_bool,
                                    name        = name,
                                    attr_int    = int(value))
        elif type(value) == type(''):
            result = update.execute(type        = self.attrib_type_string,
                                    name        = name,
                                    attr_string = value)
        else:
            raise Exception('Unknown attribute type %s' % type(value))
        return True


    def __resource_parent_add_n_children(self,
                                         connection,
                                         resource_id,
                                         n_children):
        """
        Increases the child counter of the items that are the parent of the
        given id. n_children allows negative values.
        Warning: When using this, make sure to lock a transaction.
        """
        assert type(resource_id) == type([]) or resource_id >= 0
        assert n_children is not None

        transaction = connection.begin()

        # Get a list of parent nodes.
        parent_list = self.get_resource_parents(resource_id)
        assert parent_list is not None
        
        # Decrease the child counter of parent nodes.
        table = self._table_map['resource']
        where = None
        for parent in parent_list:
            where = or_(where, table.c.id == parent.get_id())
        values = {table.c.n_children: table.c.n_children + n_children}
        update = table.update(where, values)
        result = update.execute()

        transaction.commit()
        return True


    def __resource_add_n_children(self, resource_id, n_children):
        assert type(resource_id) == type([]) or resource_id >= 0
        assert n_children >= 0
        table  = self._table_map['resource']
        values = {table.c.n_children: table.c.n_children + n_children}
        update = table.update(table.c.id == resource_id, values = values)
        result = update.execute()


    def __add_resource1(self, connection, parent_id, resource):
        """
        Inserts the given resource into the database, under the parent
        with the given id.

        @type  parent_id: int|Resource
        @param parent_id: The id of the resource under which the new resource
                          is added, or an instance of a Resource.
        @type  resource: Resource
        @param resource: The resource that is added.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert parent_id is None or parent_id >= 0
        assert resource is not None
        parent = None
        if parent_id is not None and type(parent_id) != type(0):
            parent    = parent_id
            parent_id = parent.get_id()
            if parent_id is None:
                raise AttributeError('The given parent does not exist')

        self._sql_cache_flush()
        transaction = connection.begin()

        # Retrieve information about the parent, if any. Also, increase the
        # child counter of the parent.
        if parent_id is None:
            parent_path = ResourcePath()
        else:
            parent_path = self.get_resource_path_from_id(parent_id)
            if parent_path is None:
                err = 'The given parent does not exist'
                raise AttributeError(err)
            if len(parent_path) * 8 > 252:
                err = 'Too many levels of nesting.'
                raise AttributeError(err)
            if parent is None:
                parent = self.get_resource(id = parent_id)
            if not parent.is_group():
                err = 'parent.is_group() must return True when adding a child'
                raise AttributeError(err)
            self.__resource_add_n_children(parent_id, 1)

        # If the resource already has an ID, it *should* exist in the database
        # most of the time - but we want to forgive the user even if it does
        # not.
        resource_id = resource.get_id()
        existing    = None
        if resource_id > 0:
            existing = self.get_resource(id = resource_id)
        
        # Create or update the resource.
        if existing is not None:
            self.save_resource(resource)
        else:
            table  = self._table_map['resource']
            insert = table.insert()
            result = insert.execute(resource_type = resource.__class__.__name__,
                                    handle        = resource.get_handle(),
                                    name          = resource.get_name(),
                                    is_group      = resource.is_group())
            resource_id = result.last_inserted_ids()[0]

            # Save the attributes.
            attrib_list = resource.get_attribute_list()
            for attrib_name in attrib_list.keys():
                value = attrib_list[attrib_name]
                self.__resource_add_attribute(resource_id, attrib_name, value)

        # Add a new node into the tree.
        table    = self._table_map['resource_path']
        insert   = table.insert()
        bin_path = parent_path.bin() + int2bin(0)
        result   = insert.execute(path        = bin_path,
                                  resource_id = resource_id)
        path_id  = result.last_inserted_ids()[0]

        # Assign the correct path to the new node.
        bin_path = parent_path.bin() + int2bin(path_id)
        depth    = len(parent_path) + 1
        update   = table.update(table.c.resource_id == resource_id)
        result   = update.execute(path = bin_path, depth = depth)
        
        # Add a link to every ancestor of the new node into a map.
        while len(parent_path) != 0:
            parent_id = parent_path.get_current_id()
            #print "Path:", parent_path.get(), "ID:", parent_id
            #print 'Mapping', path_id, 'to', parent_id
            insert    = self._table_map['path_ancestor_map'].insert()
            result    = insert.execute(resource_path_id = path_id,
                                       ancestor_path_id = parent_id)
            parent_path = parent_path.crop()

        transaction.commit()
        return resource_id


    def add_resource(self, parent_id, resources):
        """
        Inserts the given resources into the database, under the parent
        with the given id.

        @type  parent_id: int|Resource
        @param parent_id: The id of the resource under which the new resource
                          is added, or an instance of a Resource.
        @type  resources: Resource|list[Resource]
        @param resources: The resource that is added.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        if parent_id is not None \
          and not isinstance(parent_id, Resource) \
          and type(parent_id) != type(1):
            ptype = type(parent_id).__name__
            err   = 'parent_id must be None, Resource or int, is %s' % ptype
            raise AttributeError(err)
        if resources is None:
            raise AttributeError('resources argument must not be None')
        if type(resources) != type(list):
            resources = [resources]

        connection  = self.db.connect()
        transaction = connection.begin()
        ids         = []
        for resource in resources:
            id = self.__add_resource1(connection, parent_id, resource)
            ids.append(id)
        transaction.commit()
        connection.close()
        for n, resource in enumerate(resources):
            resource.set_id(ids[n])

        return True


    def __save_resource1(self, connection, resource):
        """
        Updates the given resource in the database.

        @type  resource: Resource
        @param resource: The resource that is saved.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert resource          is not None
        assert resource.get_id() is not None
        self._sql_cache_flush()

        transaction = connection.begin()

        table  = self._table_map['resource']
        update = table.update(table.c.id == resource.get_id())
        result = update.execute(resource_type = resource.__class__.__name__,
                                handle        = resource.get_handle(),
                                name          = resource.get_name(),
                                is_group      = resource.is_group())

        # Save the attributes.
        attrib_list = resource.get_attribute_list()
        for attrib_name in attrib_list.keys():
            value = attrib_list[attrib_name]
            self.__resource_add_attribute(resource.get_id(),
                                          attrib_name,
                                          value)
            
        transaction.commit()
        return True


    def save_resource(self, resources):
        """
        Updates the given resources in the database. Does nothing
        to any resource that does not yet exist.

        @type  resources: Resource|list[Resource]
        @param resources: The resource that is saved.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        if resources is None:
            raise AttributeError('resources argument must not be None')
        if type(resources) != type(list):
            resources = [resources]

        connection  = self.db.connect()
        transaction = connection.begin()
        for resource in resources:
            id = self.__save_resource1(connection, resource)
        transaction.commit()
        connection.close()

        return True


    def delete_resource(self, resources):
        """
        Convenience wrapper around delete_resource_from_match().

        @type  resources: Resource|list[Resource]
        @param resources: The resource that is deleted.
        @rtype:  int
        @return: The number of deleted resources.
        """
        if resources is None:
            raise AttributeError('resource argument must not be None')
        if type(resources) != type([]):
            resources = [resources]
        ids = [resource.get_id() for resource in resources]
        res = self.delete_resource_from_match(id = ids)
        for resource in resources:
            resource.set_id(None)
        return res


    def __delete_resource_from_id(self, resource_ids):
        """
        Deletes the resource with the given id (including all children)
        from the database.

        @type  resource_ids: int|list[int]
        @param resource_ids: The ids of the resources that are deleted.
        @rtype:  int
        @return: The number of deleted resources.
        """
        assert resource_ids >= 0
        if type(resource_ids) == type(0):
            resource_ids = [resource_ids]
        if len(resource_ids) == 0:
            return
        self._sql_cache_flush()

        connection  = self.db.connect()
        transaction = connection.begin()

        self.__resource_parent_add_n_children(connection, resource_ids, -1)

        # Get a list of all children.
        tbl_p1   = self._table_map['resource_path'].alias('p1')
        tbl_m    = self._table_map['path_ancestor_map']
        tbl_p2   = self._table_map['resource_path'].alias('p2')
        table    = tbl_p1.outerjoin(tbl_m,
                                    tbl_p1.c.id == tbl_m.c.ancestor_path_id)
        table    = table.outerjoin(tbl_p2,
                                   tbl_p2.c.id == tbl_m.c.resource_path_id)
        where    = None
        for id in resource_ids:
            where = or_(where, tbl_p1.c.resource_id == id)
        children = select([tbl_p2.c.resource_id],
                          where,
                          from_obj = [table])

        # Delete the children. FIXME: This is a workaround for the bug
        # in MySQL mentioned below. In later versions we will be able
        # to do this with one query.
        table  = self._table_map['resource']
        where  = table.c.id.in_(children)
        delete = table.delete(where)
        result = delete.execute()
        affect = result.rowcount

        #FIXME: There is a bug in MySQL 4.1 that prevents the combination
        # of DELETE and IN to work with more than one match, so here's the
        # extra query.
        # Delete the resource.
        where = None
        for id in resource_ids:
            where = or_(where, table.c.id == id)
        delete = table.delete(where)
        result = delete.execute()
        affect += result.rowcount

        transaction.commit()
        connection.close()

        return affect


    def delete_resource_from_match(self, **kwargs):
        """
        Deletes all resources that match the given criteria, including
        their children.

        @type  kwargs: dict
        @param kwargs: For a list of allowed keys see get_resources().
        @rtype:  int
        @return: The number of deleted resources.
        """
        self._sql_cache_flush()

        # If the ID is the only criteria, there is no need to do a match
        # first and we can just delete in one run.
        if len(kwargs.keys()) == 1 and kwargs.has_key('id'):
            ids = kwargs.get('id')
            if type(ids) == type(0):
                ids = [ids]
            return self.__delete_resource_from_id(ids)

        # We can not just delete the resource, we also have to update the
        # child counter of its parents. We need the resource id to look them
        # up.
        resources = self.get_resources(**kwargs)
        ids       = [resource.get_id() for resource in resources]
        return self.__delete_resource_from_id(ids)


    def __add_acl_from_id(self, actor_id, action_id, resource_id, permit):
        assert actor_id    >= 0
        assert action_id   >= 0
        assert resource_id >= 0
        assert permit == True or permit == False
        insert = self._table_map['acl'].insert()
        result = insert.execute(actor_id    = actor_id,
                                action_id   = action_id,
                                resource_id = resource_id,
                                permit      = permit)
        return result.last_inserted_ids()[0]


    def __update_acl_from_id(self, actor_id, action_id, resource_id, permit):
        assert actor_id    >= 0
        assert action_id   >= 0
        assert resource_id >= 0
        assert permit == True or permit == False
        table  = self._table_map['acl']
        update = table.update(and_(table.c.actor_id    == actor_id,
                                   table.c.action_id   == action_id,
                                   table.c.resource_id == resource_id))
        result = update.execute(permit = permit, last_change = datetime.datetime.now())
        return True


    def delete_permission_from_id(self, actor_id, action_id, resource_id):
        """
        Deletes the ACL with the given id from the database.

        @type  actor_id: int
        @param actor_id: The id of the actor whose ACL is to be deleted.
        @type  action_id: int
        @param action_id: The id of the action whose ACL is to be deleted.
        @type  resource_id: int
        @param resource_id: The id of the resource whose ACL is to be deleted.
        @rtype:  Boolean
        @return: True if the ACL existed, False otherwise.
        """
        assert actor_id    >= 0
        assert action_id   >= 0
        assert resource_id >= 0
        table  = self._table_map['acl']
        delete = table.delete(and_(table.c.actor_id    == actor_id,
                                   table.c.action_id   == action_id,
                                   table.c.resource_id == resource_id))
        result = delete.execute()
        if result.rowcount is 0:
            return False
        return True


    def delete_permission(self, actor, action, resource):
        """
        Convenience wrapper around delete_permission_from_id().

        @type  actor: int
        @param actor: The actor whose ACL is to be deleted.
        @type  action: int
        @param action: The action whose ACL is to be deleted.
        @type  resource: int
        @param resource: The resource whose ACL is to be deleted.
        @rtype:  Boolean
        @return: True if the ACL existed, False otherwise.
        """
        if actor is None:
            raise AttributeError('actor argument must not be None')
        if action is None:
            raise AttributeError('action argument must not be None')
        if resource is None:
            raise AttributeError('resource argument must not be None')
        return self.delete_permission_from_id(actor.get_id(),
                                              action.get_id(),
                                              resource.get_id())


    def __has_acl_from_id(self, actor_id, action_id, resource_id):
        assert actor_id    >= 0
        assert action_id   >= 0
        assert resource_id >= 0
        table  = self._table_map['acl']
        select = table.select(and_(table.c.actor_id    == actor_id,
                                   table.c.action_id   == action_id,
                                   table.c.resource_id == resource_id))
        result = select.execute()
        row    = result.fetchone()
        if row is None:
            return False
        return True


    def set_permission_from_id(self,
                               actor_list,
                               action_list,
                               resource_list,
                               permit):
        """
        Defines whether or not the given actors may perform the given actions
        on the given resources.

        @type  actor_list: list[Actor]
        @param actor_list: A list containing actors.
        @type  action_list: list[Action]
        @param action_list: A list containing actions.
        @type  resource_list: list[Resource]
        @param resource_list: A list containing resources.
        @type  permit: boolean
        @param permit: True to permit the given actions, False to deny them.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert actor_list    is not None
        assert action_list   is not None
        assert resource_list is not None
        if type(actor_list) == type(0):
            actor_list = [ actor_list ]
        if type(action_list) == type(0):
            action_list = [ action_list ]
        if type(resource_list) == type(0):
            resource_list = [ resource_list ]
        for actor_id in actor_list:
            for action_id in action_list:
                for resource_id in resource_list:
                    #print 'Set: %i,%i,%i' % (actor_id, action_id, resource_id)
                    if self.__has_acl_from_id(actor_id, action_id, resource_id):
                        self.__update_acl_from_id(actor_id,
                                                  action_id,
                                                  resource_id,
                                                  permit)
                    else:
                        self.__add_acl_from_id(actor_id,
                                               action_id,
                                               resource_id,
                                               permit)
        return True


    def set_permission(self, actor, action, resource, permit):
        """
        Convenience wrapper around set_permission_from_id().

        @type  actor: Actor
        @param actor: The actor whose permissions should be changed.
        @type  action: Action
        @param action: The action to permit or deny.
        @type  resource: Resource
        @param resource: The resource on which a permission should be defined.
        @type  permit: boolean
        @param permit: True to permit the given action, False to deny it.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert actor    is not None
        assert action   is not None
        assert resource is not None
        assert permit == True or permit == False

        # Copy each item into a list of ids.
        if type(actor) != type([]):
            actor_list = [actor.get_id()]
        else:
            actor_list = []
            for obj in actor:
                actor_list.append(obj.get_id())

        if type(action) != type([]):
            action_list = [action.get_id()]
        else:
            action_list = []
            for obj in action:
                action_list.append(obj.get_id())

        if type(resource) != type([]):
            resource_list = [resource.get_id()]
        else:
            resource_list = []
            for obj in resource:
                resource_list.append(obj.get_id())
        # Done.

        return self.set_permission_from_id(actor_list,
                                           action_list,
                                           resource_list,
                                           permit)


    def grant_from_id(self, actor_list, action_list, resource_list):
        """
        Convenience wrapper around set_permission_from_id().

        @type  actor_list: list[Actor]
        @param actor_list: A list containing actors.
        @type  action_list: list[Action]
        @param action_list: A list containing actions.
        @type  resource_list: list[Resource]
        @param resource_list: A list containing resources.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert actor_list    is not None
        assert action_list   is not None
        assert resource_list is not None
        return self.set_permission_from_id(actor_list,
                                           action_list,
                                           resource_list,
                                           True)


    def grant(self, actor, action, resource):
        """
        Convenience wrapper around set_permission().

        @type  actor: Actor
        @param actor: The actor whose permissions should be changed.
        @type  action: Action
        @param action: The action to permit.
        @type  resource: Resource
        @param resource: The resource on which a permission should be defined.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert actor    is not None
        assert action   is not None
        assert resource is not None
        return self.set_permission(actor, action, resource, True)


    def deny_from_id(self, actor_list, action_list, resource_list):
        """
        Convenience wrapper around set_permission_from_id().

        @type  actor_list: list[Actor]
        @param actor_list: A list containing actors.
        @type  action_list: list[Action]
        @param action_list: A list containing actions.
        @type  resource_list: list[Resource]
        @param resource_list: A list containing resources.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert actor_list    is not None
        assert action_list   is not None
        assert resource_list is not None
        return self.set_permission_from_id(actor_list,
                                           action_list,
                                           resource_list,
                                           False)


    def deny(self, actor, action, resource):
        """
        Convenience wrapper around set_permission().

        @type  actor: Actor
        @param actor: The actor whose permissions should be changed.
        @type  action: Action
        @param action: The action to deny.
        @type  resource: Resource
        @param resource: The resource on which a permission should be defined.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert actor    is not None
        assert action   is not None
        assert resource is not None
        return self.set_permission(actor, action, resource, False)
