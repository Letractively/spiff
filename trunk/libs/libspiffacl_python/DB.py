from DBReader  import *
from functions import int2hex

class DB(DBReader):
    def __get_resource_path_from_id(self, id):
        assert id is not None
        query = SqlQuery(self._table_names, '''
            SELECT HEX(path) path
            FROM   {t_resource_path}
            WHERE  resource_id={id}''')
        query.set_int('id', id)
        result = self.db.execute(query.get_sql())
        assert result is not None
        row = result.shift()
        if not row: return None
        length = row[0].len()
        path   = row[0][0:length - 2]
        return path


    def install(self):
        """
        Installs (or upgrades) database tables.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        #FIXME
        return True


    def uninstall(self):
        """
        Drops all tables from the database. Use with care.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        #FIXME
        return True


    def clear_database(self):
        """
        Drops the content of any database table used by this library.
        Use with care.

        Wipes out everything, including sections, actions, resources and acls.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        query = SqlQuery(self._table_names, 'DELETE FROM {t_action_section}')
        self.db.execute(query.get_sql())
        query.set_sql('DELETE FROM {t_resource_section}')
        result = self.db.execute(query.get_sql())
        assert result is not None
        return True


    def __add_object_section(self, table, section):
        assert table is 'action_section' or table is 'resource_section'
        assert section is not None
        query = SqlQuery(self._table_names, '''
            INSERT INTO {t_''' + table + '''}
              (handle, name)
            VALUES
              ({handle}, {name})''')
        query.set_string('handle', section.get_handle())
        query.set_string('name',   section.get_name())
        result = self.db.execute(query.get_sql())
        assert result is not None
        section.set_id(self.db.last_insert_id())
        return True


    def __save_object_section(self, table, section):
        assert table is 'action_section' or table is 'resource_section'
        assert section is not None
        query = SqlQuery(self._table_names, '''
            UPDATE {t_''' + table + '''}
            SET    handle={handle}, name={name}
            WHERE  id={id}''')
        query.set_int('id', section.get_id())
        query.set_string('handle', section.get_handle())
        query.set_string('name',   section.get_name())
        result = self.db.execute(query.get_sql())
        assert result is not None
        return True


    def __delete_object_section(self, table, section):
        assert table is 'action_section' or table is 'resource_section'
        assert section is not None
        query = SqlQuery(self._table_names, '''
            DELETE FROM {t_''' + table + '''}
            WHERE handle={handle}''')
        query.set_string('handle', section.get_handle())
        result = self.db.execute(query.get_sql())
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


    def add_action(action, section):
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
        query = SqlQuery(self._table_names, '''
            INSERT INTO {t_action}
              (section_handle, handle, name)
            VALUES
              ({section_handle}, {handle}, {name})''')
        query.set_string('section_handle', section.get_handle())
        query.set_string('handle',         action.get_handle())
        query.set_string('name',           action.get_name())
        result = self.db.execute(query.get_sql())
        assert result is not None
        action.set_id(self.db.last_insert_id)


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
        query = SqlQuery(self._table_names, '''
            UPDATE {t_action}
            SET section_handle={section_handle},
                handle={handle},
                name={name}
            WHERE id={id}''')
        query.set_int('id', action.get_id())
        query.set_string('section_handle', section.get_handle())
        query.set_string('handle',         action.get_handle())
        query.set_string('name',           action.get_name())
        result = self.db.execute(query.get_sql())
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
        query = SqlQuery(self._table_names, '''
            DELETE FROM {t_action}
            WHERE id={action_id}''')
        query.set_int('id', action_id)
        result = self.db.execute(query.get_sql())
        assert result is not None
        if self.db.affected_rows is 0:
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
        query = SqlQuery(self._table_names, '''
            DELETE FROM {t_action}
            WHERE section_handle={section_handle}
            AND   handle={handle}''')
        query.set_string('section_handle', section_handle)
        query.set_string('handle',         handle)
        result = self.db.execute(query.get_sql())
        assert result is not None
        if self.db.affected_rows is 0:
            return False
        return True


    def delete_action(self, action, section):
        """
        Convenience wrapper around delete_action_from_handle().

        @type  action: Action
        @param action: The action to be removed.
        @type  section: ActionSection
        @param section: The associated section.
        @rtype:  Boolean
        @return: True if the action existed, False otherwise.
        """
        assert action  is not None
        assert section is not None
        handle         = action.get_handle()
        section_handle = section.get_handle()
        if self.delete_action_from_handle(handle, section_handle):
            action.set_id(-1)
            return True
        return False


    def __resource_has_attribute(self, resource_id, name):
        assert resource_id >= 0
        assert name is not None
        query = SqlQuery(self._table_names, '''
            SELECT id
            FROM {t_resource_attribute}
            WHERE resource_id={resource_id}
            AND   name={name}''')
        query.set_int('resource_id', resource_id)
        query.set_string('name', name)
        result = self.db.execute(query.get_sql())
        assert result is not None
        row = result.shift()
        if row is not None: return True
        return False


    def __resource_add_attribute(self, resource_id, name, value):
        assert resource_id >= 0
        assert name is not None
        query = SqlQuery(self._table_names, '''
            INSERT INTO {t_resource_attribute}
              (resource_id, name, type, attr_string, attr_int)
            VALUES
              ({resource_id}, {name}, {type}, {attr_string}, {attr_int})''')
        query.set_int('resource_id', resource_id)
        query.set_string('name', name)
        if is_int(value):
            query.set_int('type', self.__attrib_type['int'])
            query.set_int('attr_int', value)
            query.set_none('attr_string')
        elif is_string(value):
            query.set_int('type', self.__attrib_type['string'])
            query.set_string('attr_string', value)
            query.set_none('attr_int')
        result = self.db.execute(query.get_sql())
        assert result is not None
        return self.db.last_insert_id


    def __resource_update_attribute(self, resource_id, name, value):
        assert resource_id >= 0
        assert name is not None
        query = SqlQuery(self._table_names, '''
            UPDATE {t_resource_attribute}
            SET type={type},
                attr_string={attr_string},
                attr_int={attr_int}
            WHERE resource_id={resource_id}
            AND   name={name}''')
        query.set_int('resource_id', resource_id)
        query.set_string('name', name)
        if is_int(value):
            query.set_int('type', self.__attrib_type['int'])
            query.set_int('attr_int', value)
            query.set_none('attr_string')
        elif is_string(value):
            query.set_int('type', self.__attrib_type['string'])
            query.set_string('attr_string', value)
            query.set_none('attr_int')
        result = self.db.execute(query.get_sql())
        assert result is not None
        return True


    def __resource_add_n_children(self, resource, n):
        assert resource is not None
        assert n >= 0
        query = SqlQuery(self._table_names, '''
            UPDATE {t_resource_path}
            SET n_children=n_children + ({n_children})
            WHERE resource_id={resource_id}''')
        query.set_int('resource_id', resource_id)
        query.set_int('n_children',  n_children)
        result = self.db.execute(query.get_sql())
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
        assert parent_id >= 0
        assert resource is not None
        assert section  is not None

        transaction = self.db.begin()

        if parent_id is None:
            parent_path = ''
        else:
            parent_path = self.__get_resource_path_from_id(parent_id)
            assert parent_path.len() / 2 <= 252
            parent      = self.get_resource_from_id(parent_id)
            assert parent.is_group()
            self.__resource_add_n_children(parent_id, 1)

        # Create the resource.
        query = SqlQuery(self._table_names, '''
            INSERT INTO {t_resource}
              (section_handle, handle, name, is_actor, is_group)
            VALUES
              ({section_handle}, {handle}, {name}, {is_actor}, {is_group})''')
        query.set_string('section_handle', section.get_handle())
        query.set_string('handle',         resource.get_handle())
        query.set_string('name',           resource.get_name())
        query.set_bool('is_actor',         resource.is_actor())
        query.set_bool('is_group',         resource.is_group())
        result = self.db.execute(query.get_sql())
        assert result is not None
        resource_id = self.db.last_insert_id

        # Add a new node into the tree.
        query = SqlQuery(self._table_names, '''
            INSERT INTO {t_resource_path}
              (path, resource_id)
            VALUES
              ({path}, {resource_id})''')
        query.set_hex('path',        parent_path + '0000000000');
        query.set_int('resource_id', resource_id)
        result = self.db.execute(query.get_sql())
        assert result is not None
        path_id = self.db.last_insert_id

        # Assign the correct path to the new node.
        query = SqlQuery(self._table_names, '''
            UPDATE {t_resource_path}
            SET path={path},
                depth={depth}
            WHERE resource_id={resource_id}''')
        path  = parent_path + int2hex(path_id, 8)
        depth = path.len() / 8
        query.set_hex('path',        path + '00')
        query.set_int('depth',       depth)
        query.set_int('resource_id', resource_id)
        result = self.db.execute(query.get_sql())
        assert result is not None
        
        # Add a link to every ancestor of the new node into a map.
        while parent_path is not '':
            query = SqlQuery(self._table_names, '''
                INSERT INTO {t_path_ancestor_map}
                  (resource_path, ancestor_path)
                VALUES
                  ({resource_path}, {ancestor_path})''')
            query.set_hex('resource_path', path        + '00')
            query.set_hex('ancestor_path', parent_path + '00')
            result = self.db.execute(query.get_sql())
            assert result is not None
            parent_path = parent_path[0:path.len() - 8]

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

        transaction = self.db.begin()

        query = SqlQuery(self._table_names, '''
            UPDATE {t_resource}
            SET section_handle={section_handle},
                handle={handle},
                name={name},
                is_actor={is_actor},
                is_group={is_group}
            WHERE id={id}''')
        query.set_id('id', resource.get_id())
        query.set_string('section_handle', section.get_handle())
        query.set_string('handle',         resource.get_handle())
        query.set_string('name',           resource.get_name())
        query.set_bool('is_actor',         resource.is_actor())
        query.set_bool('is_group',         resource.is_group())
        result = self.db.execute(query.get_sql())
        assert result is not None

        # Save the attributes.
        attrib_list = resource.get_attribute_list()
        for attrib_name in attrib_list.keys():
            value = attrib_list[attrib_name]
            self.__resource_add_attribute(resource_id, attrib_name, value)
            
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
        query = SqlQuery(self._table_names, '''
            DELETE FROM {t_resource}
            WHERE id={resource_id}''')
        query.set_id('resource_id', resource_id)
        result = self.db.execute(query.get_sql())
        assert result is not None
        if self.db.affected_rows is 0:
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
        query = SqlQuery(self._table_names, '''
            DELETE FROM {t_resource}
            WHERE section_handle={section_handle}
            AND   handle={handle}''')
        query.set_string('section_handle', section_handle)
        query.set_string('handle',         handle)
        result = self.db.execute(query.get_sql())
        assert result is not None
        if self.db.affected_rows is 0:
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
        return self.delete_resource_from_id(resource.get_id())


    def __add_acl_from_id(self, actor_id, action_id, resource_id, permit):
        assert actor_id    >= 0
        assert action_id   >= 0
        assert resource_id >= 0
        assert permit == True or permit == False
        query = SqlQuery(self._table_names, '''
            INSERT INTO {t_acl}
              (actor_id, action_id, resource_id, permit)
            VALUES
              ({actor_id}, {action_id}, {resource_id}, {permit})''')
        query.set_int('actor_id',    actor_id)
        query.set_int('action_id',   action_id)
        query.set_int('resource_id', resource_id)
        query.set_bool('permit',    permit)
        result = self.db.execute(query.get_sql())
        assert result is not None
        return self.db.last_insert_id


    def __update_acl_from_id(self, actor_id, action_id, resource_id, permit):
        assert actor_id    >= 0
        assert action_id   >= 0
        assert resource_id >= 0
        assert permit == True or permit == False
        query = SqlQuery(self._table_names, '''
            UPDATE {t_acl}
            SET   permit={permit}
            WHERE actor_id={actor_id}
            AND   action_id={action_id}
            AND   resource_id={resource_id}''')
        query.set_int('actor_id',    actor_id)
        query.set_int('action_id',   action_id)
        query.set_int('resource_id', resource_id)
        query.set_bool('permit',    permit)
        result = self.db.execute(query.get_sql())
        assert result is not None
        return True


    def __has_acl_from_id(self, actor_id, action_id, resource_id):
        assert actor_id    >= 0
        assert action_id   >= 0
        assert resource_id >= 0
        query = SqlQuery(self._table_names, '''
            SELECT id
            FROM {t_acl}
            WHERE actor_id={actor_id}
            AND   action_id={action_id}
            AND   resource_id={resource_id}''')
        query.set_int('actor_id',    actor_id)
        query.set_int('action_id',   action_id)
        query.set_int('resource_id', resource_id)
        result = self.db.execute(query.get_sql())
        assert result is not None
        row = result.shift()
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
        if same_type(actor_list, 0):
            actor_list = [ actor_list ]
        if same_type(action_list, 0):
            action_list = [ action_list ]
        if same_type(resource_list, 0):
            resource_list = [ resource_list ]
        for actor_id in actor_list:
            for action_id in action_list:
                for resource_id in resource_list:
                    if self.__has_acl_from_id(actor_id, action_id, resource_id):
                        self.__add_acl_from_id(actor_id,
                                               action_id,
                                               resource_id,
                                               permit)
                    else:
                        self.__update_acl_from_id(actor_id,
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
        return self.set_permission_from_id(actor.get_id(),
                                           action.get_id(),
                                           resource.get_id(),
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
    import sqlite
    import MySQLdb
    from sqlalchemy   import *
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
            assert db.add_action(action)
            assert action.get_id() >= 0
            action.set_name('View a User')
            assert db.save_action(action)
            assert db.delete_action_from_id(action.get_id())

            assert db.add_action(action)
            handle         = action.get_handle()
            section_handle = action_section.get_handle()
            assert db.delete_action_from_handle(handle, section_handle)

            assert db.add_action(action)
            assert db.delete_action(action, action_section)
            assert not db.delete_action(action, action_section)
            assert db.add_action(action, action_section)

            # Test Resource.
            resource = Resource('my website')
            assert db.add_resource(resource)
            assert resource.get_id() >= 0
            resource.set_name('Homepage')
            assert db.save_resource(resource)
            assert db.delete_resource_from_id(resource.get_id())

            assert db.add_resource(resource)
            handle         = resource.get_handle()
            section_handle = resource_section.get_handle()
            assert db.delete_resource_from_handle(handle, section_handle)

            assert db.add_resource(resource)
            assert db.delete_resource(resource, resource_section)
            assert not db.delete_resource(resource, resource_section)
            assert db.add_resource(resource, resource_section)

            # Test ResourceGroup.
            #FIXME

            # Test Acl.
            #FIXME

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
            print dbn
            db   = create_engine(dbn)
            self.test_with_db(db)

    testcase = DBTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
