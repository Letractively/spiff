from DBReader  import *
from functions import *
import string

class DB(DBReader):
    def __get_resource_path_from_id(self, id):
        assert id is not None
        table  = self._table_map['resource_path']
        query  = select([table.c.path],
                        table.c.resource_id == id,
                        from_obj = [table])
        result = query.execute()
        assert result is not None
        row = result.fetchone()
        if not row: return None
        length = len(row['path'])
        path   = bin_path2hex_path(row['path']) #[0:length - 2]
        return path


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

        Wipes out everything, including sections, actions, resources and acls.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        delete = self._table_map['action_section'].delete()
        result = delete.execute()
        assert result is not None
        delete = self._table_map['resource_section'].delete()
        result = delete.execute()
        assert result is not None
        return True


    def __add_object_section(self, table, section):
        assert table is 'action_section' or table is 'resource_section'
        assert section is not None
        insert = self._table_map[table].insert()
        result = insert.execute(handle = section.get_handle(),
                                name   = section.get_name())
        assert result is not None
        section.set_id(result.last_inserted_ids()[0])
        return True


    def __save_object_section(self, table_name, section):
        assert table_name is 'action_section' \
            or table_name is 'resource_section'
        assert section is not None
        table  = self._table_map[table_name]
        update = table.update(table.c.id == section.get_id())
        result = update.execute(handle = section.get_handle(),
                                name   = section.get_name())
        assert result is not None
        return True


    def __delete_object_section(self, table, section):
        assert table is 'action_section' or table is 'resource_section'
        assert section is not None
        delete = self._table_map[table].delete()
        result = delete.execute(handle = section.get_handle())
        assert result is not None
        section.set_id(-1)
        return True


    def add_action_section(self, section):
        """
        Insert the given action section into the database.

        @type  section: ActionSection
        @param section: The section to be inserted.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert section is not None
        return self.__add_object_section('action_section', section)


    def save_action_section(self, section):
        """
        Updates the given action section in the database.

        @type  section: ActionSection
        @param section: The section to be saved.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert section is not None
        return self.__save_object_section('action_section', section)


    def delete_action_section(self, section):
        """
        Deletes the given action section from the database.
        All associated actions and ACLs will be deleted. Use with care!

        @type  section: ActionSection
        @param section: The section to be deleted.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert section is not None
        return self.__delete_object_section('action_section', section)


    def add_resource_section(self, section):
        """
        Insert the given resource section into the database.

        @type  section: ResourceSection
        @param section: The section to be inserted.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert section is not None
        return self.__add_object_section('resource_section', section)


    def save_resource_section(self, section):
        """
        Updates the given resource section in the database.

        @type  section: ResourceSection
        @param section: The section to be saved.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert section is not None
        return self.__save_object_section('resource_section', section)


    def delete_resource_section(self, section):
        """
        Deletes the given resource section from the database.
        All associated resources and ACLs will be deleted. Use with care!

        @type  section: ResourceSection
        @param section: The section to be deleted.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert section is not None
        return self.__delete_object_section('resource_section', section)


    def add_action(self, action, section):
        """
        Inserts the given action into the given section in the database.

        @type  action: Action
        @param action: The action to be added.
        @type  section: ActionSection
        @param section: The section into which the action is inserted.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert action  is not None
        assert section is not None
        insert = self._table_map['action'].insert()
        result = insert.execute(section_handle = section.get_handle(),
                                handle         = action.get_handle(),
                                name           = action.get_name())
        assert result is not None
        action.set_id(result.last_inserted_ids()[0])
        return True


    def save_action(self, action, section):
        """
        Updates the given action in the database.

        @type  action: Action
        @param action: The action to be saved.
        @type  section: ActionSection
        @param section: The section into which the action is inserted.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert action  is not None
        assert section is not None
        table  = self._table_map['action']
        update = table.update(table.c.id == action.get_id())
        result = update.execute(section_handle = section.get_handle(),
                                handle         = action.get_handle(),
                                name           = action.get_name())
        assert result is not None
        return True


    def delete_action_from_id(self, action_id):
        """
        Deletes the action with the given id from the database.
        All ACLs associated with the action are removed.

        @type  action_id: int
        @param action_id: The id of the action to be removed.
        @rtype:  Boolean
        @return: True if the action existed, False otherwise.
        """
        assert action_id is not None
        delete = self._table_map['action'].delete()
        result = delete.execute(id = action_id)
        assert result is not None
        if result.rowcount is 0:
            return False
        return True


    def delete_action_from_handle(self, handle, section_handle):
        """
        Deletes the action with the given handle in the section with the
        given section handle from the database.
        All ACLs associated with the action are removed.

        @type  handle: string
        @param handle: The handle of the action to be removed.
        @type  section_handle: string
        @param section_handle: The handle of the associated section.
        @rtype:  Boolean
        @return: True if the action existed, False otherwise.
        """
        assert handle         is not None
        assert section_handle is not None
        delete = self._table_map['action'].delete()
        result = delete.execute(section_handle = section_handle,
                                handle         = handle)
        assert result is not None
        if int(result.rowcount) is 0:
            return False
        return True


    def delete_action(self, action):
        """
        Convenience wrapper around delete_action_from_handle().

        @type  action: Action
        @param action: The action to be removed.
        @rtype:  Boolean
        @return: True if the action existed, False otherwise.
        """
        assert action is not None
        assert action.get_id() >= 0
        res = self.delete_action_from_id(action.get_id())
        action.set_id(-1)
        return res


    def __resource_has_attribute(self, resource_id, name):
        assert resource_id >= 0
        assert name is not None
        table  = self._table_map['resource_attribute']
        select = table.select(and_(table.c.resource_id == resource_id,
                                   table.c.name        == name))
        result = select.execute()
        assert result is not None
        row = result.fetchone()
        if row is not None: return True
        return False


    def __resource_add_attribute(self, resource_id, name, value):
        assert resource_id >= 0
        assert name is not None
        insert = self._table_map['resource_attribute'].insert()
        try:
            int(value)
            is_int = True
        except:
            is_int = False
        if is_int:
            result = insert.execute(resource_id = resource_id,
                                    name        = name,
                                    type        = self.attrib_type_int,
                                    attr_int    = value)
        else:
            result = insert.execute(resource_id = resource_id,
                                    name        = name,
                                    type        = self.attrib_type_int,
                                    attr_string = value)
        assert result is not None
        return result.last_inserted_ids()[0]


    def __resource_update_attribute(self, resource_id, name, value):
        assert resource_id >= 0
        assert name is not None
        table  = self._table_map['resource_attribute']
        update = table.update(and_(table.c.resource_id == resource_id,
                                   table.c.name        == name))
        try:
            int(value)
            is_int = True
        except:
            is_int = False
        if is_int:
            result = update.execute(type  = self.attrib_type_int,
                                    name  = name,
                                    value = value)
        else:
            result = update.execute(type  = self.attrib_type_string,
                                    name  = name,
                                    value = value)
        assert result is not None
        return True


    def __resource_add_n_children(self, resource_id, n_children):
        assert resource_id >= 0
        assert n_children  >= 0
        table  = self._table_map['resource_path']
        update = table.update(table.c.resource_id == resource_id)
        result = update.execute(n_children = table.c.n_children + n_children)
        assert result is not None


    def add_resource(self, parent_id, resource, section):
        """
        Inserts the given rescource into the given section of the database,
        under the parent with the given id.

        @type  parent_id: int
        @param parent_id: The id of the resource under which the new resource
                          is added.
        @type  resource: Resource
        @param resource: The resource that is added.
        @type  section: ResourceSection
        @param section: The associated resource section.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert parent_id is None or parent_id >= 0
        assert resource is not None
        assert section  is not None

        connection  = self.db.connect()
        transaction = connection.begin()

        if parent_id is None:
            parent_path = ''
        else:
            parent_path = self.__get_resource_path_from_id(parent_id)
            assert parent_path is not None
            assert len(parent_path) / 2 <= 252
            parent = self.get_resource_from_id(parent_id)
            assert parent.is_group()
            self.__resource_add_n_children(parent_id, 1)

        # Create the resource.
        table  = self._table_map['resource']
        insert = table.insert()
        result = insert.execute(section_handle = section.get_handle(),
                                handle         = resource.get_handle(),
                                name           = resource.get_name(),
                                is_actor       = resource.is_actor(),
                                is_group       = resource.is_group())
        assert result is not None
        resource_id = result.last_inserted_ids()[0]

        # Add a new node into the tree.
        table    = self._table_map['resource_path']
        insert   = table.insert()
        bin_path = hex_path2bin_path(parent_path + '00000000')
        result   = insert.execute(path        = bin_path,
                                  resource_id = resource_id)
        assert result is not None
        path_id = result.last_inserted_ids()[0]

        # Assign the correct path to the new node.
        path     = parent_path + int2hex(path_id, 8)
        bin_path = hex_path2bin_path(path)
        depth    = len(path) / 8
        update   = table.update(table.c.resource_id == resource_id)
        result   = update.execute(path = bin_path, depth = depth)
        assert result is not None
        
        # Add a link to every ancestor of the new node into a map.
        while parent_path is not '':
            parent_id = string.atol(parent_path[-8:], 16)
            #print "Path:", parent_path[-8:], "ID:", parent_id
            #print 'Mapping', path_id, 'to', parent_id
            insert    = self._table_map['path_ancestor_map'].insert()
            result    = insert.execute(resource_path_id = path_id,
                                       ancestor_path_id = parent_id)
            assert result is not None
            parent_path = parent_path[0:len(parent_path) - 8]

        # Save the attributes.
        attrib_list = resource.get_attribute_list()
        for attrib_name in attrib_list.keys():
            value = attrib_list[attrib_name]
            self.__resource_add_attribute(resource_id, attrib_name, value)
            
        transaction.commit()
        resource.set_id(resource_id)
        return True


    def save_resource(self, resource, section):
        """
        Updates the given rescource in the given section of the database.

        @type  resource: Resource
        @param resource: The resource that is saved.
        @type  section: ResourceSection
        @param section: The associated resource section.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        assert resource is not None
        assert section  is not None

        connection  = self.db.connect()
        transaction = connection.begin()

        table  = self._table_map['resource']
        update = table.update(table.c.id == resource.get_id())
        result = update.execute(section_handle = section.get_handle(),
                                handle         = resource.get_handle(),
                                name           = resource.get_name(),
                                is_actor       = resource.is_actor(),
                                is_group       = resource.is_group())
        assert result is not None

        # Save the attributes.
        attrib_list = resource.get_attribute_list()
        for attrib_name in attrib_list.keys():
            value = attrib_list[attrib_name]
            self.__resource_add_attribute(resource.get_id(),
                                          attrib_name,
                                          value)
            
        transaction.commit()
        return True


    def delete_resource_from_id(self, resource_id):
        """
        Deletes the rescource with the given id from the database.

        @type  resource_id: int
        @param resource_id: The id of the resource that is deleted.
        @rtype:  Boolean
        @return: True if the resource existed, False otherwise.
        """
        assert resource_id >= 0
        table  = self._table_map['resource']
        delete = table.delete(table.c.id == resource_id)
        result = delete.execute()
        assert result is not None
        if result.rowcount is 0:
            return False
        return True

        
    def delete_resource_from_handle(self, handle, section_handle):
        """
        Deletes the rescource with the given handle out of the
        given section of the database.

        @type  handle: string
        @param handle: The handle of the resource that is deleted.
        @type  section: string
        @param section: The handle of the associated resource section.
        @rtype:  Boolean
        @return: True if the resource existed, False otherwise.
        """
        assert handle         is not None
        assert section_handle is not None
        table  = self._table_map['resource']
        delete = table.delete(and_(table.c.section_handle == section_handle,
                                   table.c.handle         == handle))
        result = delete.execute()
        assert result is not None
        if result.rowcount is 0:
            return False
        return True


    def delete_resource(self, resource):
        """
        Convenience wrapper around delete_resource_from_id().

        @type  resource: Resource
        @param resource: The resource that is deleted.
        @rtype:  Boolean
        @return: True if the resource existed, False otherwise.
        """
        assert resource is not None
        assert resource.get_id() >= 0
        res = self.delete_resource_from_id(resource.get_id())
        resource.set_id(-1)
        return res


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
        assert result is not None
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
        result = update.execute(permit = permit)
        assert result is not None
        return True


    def __has_acl_from_id(self, actor_id, action_id, resource_id):
        assert actor_id    >= 0
        assert action_id   >= 0
        assert resource_id >= 0
        table  = self._table_map['acl']
        select = table.select(and_(table.c.actor_id    == actor_id,
                                   table.c.action_id   == action_id,
                                   table.c.resource_id == resource_id))
        result = select.execute()
        assert result is not None
        row = result.fetchone()
        if row is None: return False
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


if __name__ == '__main__':
    import unittest
    import MySQLdb
    from ConfigParser import RawConfigParser

    class DBTest(unittest.TestCase):
        def test_with_db(self, db):
            assert db is not None
            db = DB(db)
            assert db.uninstall()
            assert db.install()

            # Test ActionSection.
            action_section = ActionSection('user permissions')
            assert db.add_action_section(action_section)
            assert action_section.get_id() >= 0
            action_section.set_name('User Permissions')
            assert db.save_action_section(action_section)
            assert db.delete_action_section(action_section)
            assert db.add_action_section(action_section)

            # Test ResourceSection.
            resource_section = ResourceSection('users')
            assert db.add_resource_section(resource_section)
            assert resource_section.get_id() >= 0
            resource_section.set_name('Users')
            assert db.save_resource_section(resource_section)
            assert db.delete_resource_section(resource_section)
            assert db.add_resource_section(resource_section)

            # Test Action.
            action = Action('view user')
            assert db.add_action(action, action_section)
            assert action.get_id() >= 0
            action.set_name('View a User')
            assert db.save_action(action, action_section)
            assert db.delete_action_from_id(action.get_id())

            assert db.add_action(action, action_section)
            handle         = action.get_handle()
            section_handle = action_section.get_handle()
            assert db.delete_action_from_handle(handle, section_handle)

            assert db.add_action(action, action_section)
            assert db.delete_action(action)
            assert action.get_id() < 0
            assert db.add_action(action, action_section)

            # Test Resource.
            website = Resource('my website')
            assert db.add_resource(None, website, resource_section)
            assert website.get_id() >= 0
            website.set_name('Homepage')
            assert db.save_resource(website, resource_section)
            assert db.delete_resource_from_id(website.get_id())

            assert db.add_resource(None, website, resource_section)
            handle         = website.get_handle()
            section_handle = resource_section.get_handle()
            assert db.delete_resource_from_handle(handle, section_handle)

            assert db.add_resource(None, website, resource_section)
            assert db.delete_resource(website)
            assert website.get_id() < 0

            # Test ResourceGroup.
            homepage = ResourceGroup('my website')
            assert db.add_resource(None, homepage, resource_section)
            assert homepage.get_id() >= 0
            homepage.set_name('Homepage')
            assert db.save_resource(homepage, resource_section)

            child_page = Resource('my child site')
            assert db.add_resource(homepage.get_id(),
                                   child_page,
                                   resource_section)
            assert child_page.get_id() >= 0
            child_page.set_name('Child Page')
            assert db.save_resource(child_page, resource_section)
            assert db.delete_resource_from_id(child_page.get_id())
            assert db.add_resource(homepage.get_id(),
                                   child_page,
                                   resource_section)

            children = db.get_resource_children_from_id(homepage.get_id())
            assert children is not None
            assert len(children) == 1
            children = db.get_resource_children(homepage)
            assert children is not None
            assert len(children) == 1

            parents = db.get_resource_parents_from_id(child_page.get_id())
            assert parents is not None
            assert len(parents) == 1
            parents = db.get_resource_parents(child_page)
            assert parents is not None
            assert len(parents) == 1

            # Test ActorGroup.
            actor = ActorGroup('Administrators')
            assert db.add_resource(None, actor, resource_section)
            assert actor.get_id() >= 0
            actor.set_name('Admin Users')
            assert db.save_resource(actor, resource_section)

            sub_resource = Actor('Admin')
            assert db.add_resource(actor.get_id(),
                                   sub_resource,
                                   resource_section)
            assert sub_resource.get_id() >= 0
            sub_resource.set_name('Admin User')
            assert db.save_resource(sub_resource, resource_section)
            assert db.delete_resource_from_id(sub_resource.get_id())
            assert db.add_resource(actor.get_id(),
                                   sub_resource,
                                   resource_section)

            # ***********************************
            # * ACL tests below.
            # ***********************************
            assert db.clear_database()

            # Set up sections.
            action_section  = ActionSection('user permissions')
            user_section    = ResourceSection('Users')
            content_section = ResourceSection('Content')
            assert db.add_action_section(action_section)
            assert db.add_resource_section(user_section)
            assert db.add_resource_section(content_section)

            # Set up actions.
            view = Action('View Content')
            assert db.add_action(view, action_section)
            edit = Action('Edit Content')
            assert db.add_action(edit, action_section)
            delete = Action('Delete Content')
            assert db.add_action(delete, action_section)

            # Set up content.
            homepage         = ResourceGroup('Homepage')
            sub_page_1       = ResourceGroup('Sub Page 1')
            sub_page_1_1     = ResourceGroup('Sub Page 1.1')
            sub_page_1_1_1   = ResourceGroup('Sub Page 1.1.1')
            sub_page_1_1_1_1 = ResourceGroup('Sub Page 1.1.1.1')
            sub_page_1_2     = ResourceGroup('Sub Page 1.2')
            sub_page_2       = ResourceGroup('Sub Page 2')
            assert db.add_resource(None, homepage, content_section)
            assert db.add_resource(homepage.get_id(),
                                   sub_page_1,
                                   content_section)
            assert db.add_resource(sub_page_1.get_id(),
                                   sub_page_1_1,
                                   content_section)
            assert db.add_resource(sub_page_1_1.get_id(),
                                   sub_page_1_1_1,
                                   content_section)
            assert db.add_resource(sub_page_1_1.get_id(),
                                   sub_page_1_1_1_1,
                                   content_section)
            assert db.add_resource(sub_page_1.get_id(),
                                   sub_page_1_2,
                                   content_section)
            assert db.add_resource(homepage.get_id(),
                                   sub_page_2,
                                   content_section)

            # Set up groups.
            users  = ActorGroup('Users')
            admins = ActorGroup('Amins')
            assert db.add_resource(None, users,  resource_section)
            assert db.add_resource(None, admins, resource_section)
            
            # Set up users.
            user = Actor('Normal User')
            assert db.add_resource(users.get_id(),  user,  resource_section)
            anon = Actor('Anonymous User')
            assert db.add_resource(users.get_id(),  anon,  resource_section)
            admin = Actor('Administrator')
            assert db.add_resource(admins.get_id(), admin, resource_section)
            
            # Set up ACLs.
            db.grant(admins, [view, edit, delete], homepage)
            db.grant(users,  view,                 homepage)
            db.grant(user,   edit,                 sub_page_1)
            db.deny(anon,    view,                 sub_page_1)

            # Test Acl.
            assert db.has_permission(admin, view, homepage)
            assert db.has_permission(admin, view, sub_page_1)
            assert db.has_permission(admin, view, sub_page_1_1)
            assert db.has_permission(admin, view, sub_page_1_1_1)
            assert db.has_permission(admin, view, sub_page_1_1_1_1)
            assert db.has_permission(admin, view, sub_page_1_2)
            assert db.has_permission(admin, view, sub_page_2)

            assert db.has_permission(admin, edit, homepage)
            assert db.has_permission(admin, edit, sub_page_1)
            assert db.has_permission(admin, edit, sub_page_1_1)
            assert db.has_permission(admin, edit, sub_page_1_1_1)
            assert db.has_permission(admin, edit, sub_page_1_1_1_1)
            assert db.has_permission(admin, edit, sub_page_1_2)
            assert db.has_permission(admin, edit, sub_page_2)

            assert db.has_permission(admin, delete, homepage)
            assert db.has_permission(admin, delete, sub_page_1)
            assert db.has_permission(admin, delete, sub_page_1_1)
            assert db.has_permission(admin, delete, sub_page_1_1_1)
            assert db.has_permission(admin, delete, sub_page_1_1_1_1)
            assert db.has_permission(admin, delete, sub_page_1_2)
            assert db.has_permission(admin, delete, sub_page_2)

            assert db.has_permission(user, view, homepage)
            assert db.has_permission(user, view, sub_page_1)
            assert db.has_permission(user, view, sub_page_1_1)
            assert db.has_permission(user, view, sub_page_1_1_1)
            assert db.has_permission(user, view, sub_page_1_1_1_1)
            assert db.has_permission(user, view, sub_page_1_2)
            assert db.has_permission(user, view, sub_page_2)

            assert not db.has_permission(user, edit, homepage)
            assert db.has_permission(user, edit, sub_page_1)
            assert db.has_permission(user, edit, sub_page_1_1)
            assert db.has_permission(user, edit, sub_page_1_1_1)
            assert db.has_permission(user, edit, sub_page_1_1_1_1)
            assert db.has_permission(user, edit, sub_page_1_2)
            assert not db.has_permission(user, edit, sub_page_2)

            assert not db.has_permission(user, delete, homepage)
            assert not db.has_permission(user, delete, sub_page_1)
            assert not db.has_permission(user, delete, sub_page_1_1)
            assert not db.has_permission(user, delete, sub_page_1_1_1)
            assert not db.has_permission(user, delete, sub_page_1_1_1_1)
            assert not db.has_permission(user, delete, sub_page_1_2)
            assert not db.has_permission(user, delete, sub_page_2)

            assert db.has_permission(anon, view, homepage)
            assert not db.has_permission(anon, view, sub_page_1)
            assert not db.has_permission(anon, view, sub_page_1_1)
            assert not db.has_permission(anon, view, sub_page_1_1_1)
            assert not db.has_permission(anon, view, sub_page_1_1_1_1)
            assert not db.has_permission(anon, view, sub_page_1_2)
            assert db.has_permission(anon, view, sub_page_2)

            assert not db.has_permission(anon, edit, homepage)
            assert not db.has_permission(anon, edit, sub_page_1)
            assert not db.has_permission(anon, edit, sub_page_1_1)
            assert not db.has_permission(anon, edit, sub_page_1_1_1)
            assert not db.has_permission(anon, edit, sub_page_1_1_1_1)
            assert not db.has_permission(anon, edit, sub_page_1_2)
            assert not db.has_permission(anon, edit, sub_page_2)

            assert not db.has_permission(anon, delete, homepage)
            assert not db.has_permission(anon, delete, sub_page_1)
            assert not db.has_permission(anon, delete, sub_page_1_1)
            assert not db.has_permission(anon, delete, sub_page_1_1_1)
            assert not db.has_permission(anon, delete, sub_page_1_1_1_1)
            assert not db.has_permission(anon, delete, sub_page_1_2)
            assert not db.has_permission(anon, delete, sub_page_2)

            perms = db.get_permission_list_from_id(admins.get_id(),
                                                   sub_page_1_1_1.get_id())
            #for acl in perms:
            #    print 'Permission:', acl.get_action().get_name()

            # Clean up.
            assert db.clear_database()
            assert db.uninstall()


        def runTest(self):
            # Read config.
            cfg = RawConfigParser()
            cfg.read('unit_test.cfg')
            host     = cfg.get('database', 'host')
            db_name  = cfg.get('database', 'db_name')
            user     = cfg.get('database', 'user')
            password = cfg.get('database', 'password')

            # Connect to MySQL.
            auth = user + ':' + password
            dbn  = 'mysql://' + auth + '@' + host + '/' + db_name
            #print dbn
            db   = create_engine(dbn)
            self.test_with_db(db)

    testcase = DBTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
