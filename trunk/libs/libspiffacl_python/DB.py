from DBReader import *

class DB(DBReader):
    def __int2hex(self, n):
        assert n is not None
        hexval = '00000000' + n.tohex()
        return hexval[-8:]


    def __get_resource_path_from_id(self, id):
        assert id is not None
        query = SqlQuery(self.__table_names, '''
            SELECT HEX(path) path
            FROM   {t_resource_path}
            WHERE  resource_id={id}''')
        query.set_int('id', id)
        result = self.__db.execute(query.sql)
        assert result is not None
        row = result.shift()
        if not row: return None
        length = row[0].len()
        path   = row[0][0:length - 2]
        return path


    def install(self):
        #FIXME
        pass


    def clear_database(self):
        query = SqlQuery(self.__table_names, 'DELETE FROM {t_action_section}')
        self.__db.execute(query.sql)
        query.set_sql('DELETE FROM {t_resource_section}')
        result = self.__db.execute(query.sql)
        assert result is not None
        return True


    def clear_section_from_handle(self, handle):
        query = SqlQuery(self.__table_names, '''
            DELETE FROM {t_action_section}
            WHERE handle={handle}''')
        query.set_string('handle', handle)
        result = self.__db.execute(query.sql)
        assert result is not None
        return True


    def clear_section(self, section):
        return self.clear_section_from_handle(section.get_handle())


    def __add_object_section(self, table, section):
        assert table is 'action_section' or table is 'resource_section'
        assert section is not None
        query = SqlQuery(self.__table_names, '''
            INSERT INTO {t_''' + table + '''}
              (handle, name)
            VALUES
              ({handle}, {name})''')
        query.set_string('handle', section.get_handle())
        query.set_string('name',   section.get_name())
        result = self.__db.execute(query.sql)
        assert result is not None
        section.set_id(self.__db.last_insert_id())
        return section


    def __save_object_section(self, table, section):
        assert table is 'action_section' or table is 'resource_section'
        assert section is not None
        query = SqlQuery(self.__table_names, '''
            UPDATE {t_''' + table + '''}
            SET    handle={handle}, name={name}
            WHERE  id={id}''')
        query.set_int('id', section.get_id())
        query.set_string('handle', section.get_handle())
        query.set_string('name',   section.get_name())
        result = self.__db.execute(query.sql)
        assert result is not None
        return section


    def __delete_object_section(self, table, section):
        assert table is 'action_section' or table is 'resource_section'
        assert section is not None
        query = SqlQuery(self.__table_names, '''
            DELETE FROM {t_''' + table + '''}
            WHERE handle={handle}''')
        query.set_string('handle', section.get_handle())
        result = self.__db.execute(query.sql)
        assert result is not None
        section.set_id(-1)
        return True


    def add_action_section(self, section):
        assert section is not None
        return self.__add_object_section('action_section', section)


    def save_action_section(self, section):
        assert section is not None
        return self.__save_object_section('action_section', section)


    def delete_action_section(self, section):
        assert section is not None
        return self.__delete_object_section('action_section', section)


    def add_resource_section(self, section):
        assert section is not None
        return self.__add_object_section('resource_section', section)


    def save_resource_section(self, section):
        assert section is not None
        return self.__save_object_section('resource_section', section)


    def delete_resource_section(self, section):
        assert section is not None
        return self.__delete_object_section('resource_section', section)


    def add_action(action, section):
        assert action  is not None
        assert section is not None
        query = SqlQuery(self.__table_names, '''
            INSERT INTO {t_action}
              (section_handle, handle, name)
            VALUES
              ({section_handle}, {handle}, {name})''')
        query.set_string('section_handle', section.get_handle())
        query.set_string('handle',         action.get_handle())
        query.set_string('name',           action.get_name())
        result = self.__db.execute(query.sql)
        assert result is not None
        action.set_id(self.__db.last_insert_id)


    def save_action(self, action, section):
        assert action  is not None
        assert section is not None
        query = SqlQuery(self.__table_names, '''
            UPDATE {t_action}
            SET section_handle={section_handle},
                handle={handle},
                name={name}
            WHERE id={id}''')
        query.set_id('id', action.get_id())
        query.set_string('section_handle', section.get_handle())
        query.set_string('handle',         action.get_handle())
        query.set_string('name',           action.get_name())
        result = self.__db.execute(query.sql)
        assert result is not None
        return True


    def delete_action_from_id(self, action_id):
        assert action_id is not None
        query = SqlQuery(self.__table_names, '''
            DELETE FROM {t_action}
            WHERE id={action_id}''')
        query.set_int('id', action_id)
        result = self.__db.execute(query.sql)
        assert result is not None
        return True


    def delete_action(self, action, section):
        assert action  is not None
        assert section is not None
        query = SqlQuery(self.__table_names, '''
            DELETE FROM {t_action}
            WHERE section_handle={section_handle}
            AND   handle={handle}''')
        query.set_string('section_handle', section.get_handle())
        query.set_string('handle',         action.get_handle())
        result = self.__db.execute(query.sql)
        assert result is not None
        action.set_id(-1)
        return True


    def __resource_has_attribute(self, resource_id, name):
        assert resource_id >= 0
        assert name is not None
        query = SqlQuery(self.__table_names, '''
            SELECT id
            FROM {t_resource_attribute}
            WHERE resource_id={resource_id}
            AND   name={name}''')
        query.set_int('resource_id', resource_id)
        query.set_string('name', name)
        result = self.__db.execute(query.sql)
        assert result is not None
        row = result.shift()
        if row is not None: return True
        return False


    def __resource_add_attribute(self, resource_id, name, value):
        assert resource_id >= 0
        assert name is not None
        query = SqlQuery(self.__table_names, '''
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
        result = self.__db.execute(query.sql)
        assert result is not None
        return self.__db.last_insert_id


    def __resource_update_attribute(self, resource_id, name, value):
        assert resource_id >= 0
        assert name is not None
        query = SqlQuery(self.__table_names, '''
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
        result = self.__db.execute(query.sql)
        assert result is not None
        return True


    def __resource_add_n_children(self, resource, n):
        assert resource is not None
        assert n >= 0
        query = SqlQuery(self.__table_names, '''
            UPDATE {t_resource_path}
            SET n_children=n_children + ({n_children})
            WHERE resource_id={resource_id}''')
        query.set_int('resource_id', resource_id)
        query.set_int('n_children',  n_children)
        result = self.__db.execute(query.sql)
        assert result is not None


    def add_resource(self, parent_id, resource, section):
        assert parent_id >= 0
        assert resource is not None
        assert section  is not None

        transaction = self.__db.begin()

        if parent_id is None:
            parent_path = ''
        else:
            parent_path = self.__get_resource_path_from_id(parent_id)
            assert parent_path.len() / 2 <= 252
            parent      = self.get_resource_from_id(parent_id)
            assert parent.is_group()
            self.__resource_add_n_children(parent_id, 1)

        # Create the resource.
        query = SqlQuery(self.__table_names, '''
            INSERT INTO {t_resource}
              (section_handle, handle, name, is_actor, is_group)
            VALUES
              ({section_handle}, {handle}, {name}, {is_actor}, {is_group})''')
        query.set_string('section_handle', section.get_handle())
        query.set_string('handle',         resource.get_handle())
        query.set_string('name',           resource.get_name())
        query.set_bool('is_actor',         resource.is_actor())
        query.set_bool('is_group',         resource.is_group())
        result = self.__db.execute(query.sql)
        assert result is not None
        resource_id = self.__db.last_insert_id

        # Add a new node into the tree.
        query = SqlQuery(self.__table_names, '''
            INSERT INTO {t_resource_path}
              (path, resource_id)
            VALUES
              ({path}, {resource_id})''')
        query.set_hex('path',        parent_path + '0000000000');
        query.set_int('resource_id', resource_id)
        result = self.__db.execute(query.sql)
        assert result is not None
        path_id = self.__db.last_insert_id

        # Assign the correct path to the new node.
        query = SqlQuery(self.__table_names, '''
            UPDATE {t_resource_path}
            SET path={path},
                depth={depth}
            WHERE resource_id={resource_id}''')
        path  = parent_path + self.__int2hex(path_id)
        depth = path.len() / 8
        query.set_hex('path',        path + '00')
        query.set_int('depth',       depth)
        query.set_int('resource_id', resource_id)
        result = self.__db.execute(query.sql)
        assert result is not None
        
        # Add a link to every ancestor of the new node into a map.
        while parent_path is not '':
            query = SqlQuery(self.__table_names, '''
                INSERT INTO {t_path_ancestor_map}
                  (resource_path, ancestor_path)
                VALUES
                  ({resource_path}, {ancestor_path})''')
            query.set_hex('resource_path', path        + '00')
            query.set_hex('ancestor_path', parent_path + '00')
            result = self.__db.execute(query.sql)
            assert result is not None
            parent_path = parent_path[0:path.len() - 8]

        # Save the attributes.
        attrib_list = resource.get_attribute_list()
        for attrib_name in attrib_list.keys():
            value = attrib_list[attrib_name]
            self.__resource_add_attribute(resource_id, attrib_name, value)
            
        transaction.commit()
        resource.set_id(resource_id)
        return resource


    def save_resource(self, resource, section):
        assert resource is not None
        assert section  is not None

        transaction = self.__db.begin()

        query = SqlQuery(self.__table_names, '''
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
        result = self.__db.execute(query.sql)
        assert result is not None

        # Save the attributes.
        attrib_list = resource.get_attribute_list()
        for attrib_name in attrib_list.keys():
            value = attrib_list[attrib_name]
            self.__resource_add_attribute(resource_id, attrib_name, value)
            
        transaction.commit()
        return resource


    def delete_resource_from_id(self, resource_id):
        assert resource_id >= 0
        query = SqlQuery(self.__table_names, '''
            DELETE FROM {t_resource}
            WHERE id={resource_id}''')
        query.set_id('resource_id', resource_id)
        result = self.__db.execute(query.sql)
        assert result is not None
        return True

        
    def delete_resource_from_handle(self, handle, section_handle):
        assert handle         is not None
        assert section_handle is not None
        query = SqlQuery(self.__table_names, '''
            DELETE FROM {t_resource}
            WHERE section_handle={section_handle}
            AND   handle={handle}''')
        query.set_string('section_handle', section_handle)
        query.set_string('handle',         handle)
        result = self.__db.execute(query.sql)
        assert result is not None
        return True


    def delete_resource(self, resource, section):
        assert resource is not None
        assert section  is not None
        assert resource.get_id() >= 0
        return self.delete_resource_from_id(resource.get_id())


    def __add_acl_from_id(self, actor_id, action_id, resource_id, permit):
        assert actor_id    >= 0
        assert action_id   >= 0
        assert resource_id >= 0
        assert permit == True or permit == False
        query = SqlQuery(self.__table_names, '''
            INSERT INTO {t_acl}
              (actor_id, action_id, resource_id, permit)
            VALUES
              ({actor_id}, {action_id}, {resource_id}, {permit})''')
        query.set_int('actor_id',    actor_id)
        query.set_int('action_id',   action_id)
        query.set_int('resource_id', resource_id)
        query.set_bool('permit',    permit)
        result = self.__db.execute(query.sql)
        assert result is not None
        return self.__db.last_insert_id


    def __update_acl_from_id(self, actor_id, action_id, resource_id, permit):
        assert actor_id    >= 0
        assert action_id   >= 0
        assert resource_id >= 0
        assert permit == True or permit == False
        query = SqlQuery(self.__table_names, '''
            UPDATE {t_acl}
            SET   permit={permit}
            WHERE actor_id={actor_id}
            AND   action_id={action_id}
            AND   resource_id={resource_id}''')
        query.set_int('actor_id',    actor_id)
        query.set_int('action_id',   action_id)
        query.set_int('resource_id', resource_id)
        query.set_bool('permit',    permit)
        result = self.__db.execute(query.sql)
        assert result is not None
        return True


    def __has_acl_from_id(self, actor_id, action_id, resource_id):
        assert actor_id    >= 0
        assert action_id   >= 0
        assert resource_id >= 0
        query = SqlQuery(self.__table_names, '''
            SELECT id
            FROM {t_acl}
            WHERE actor_id={actor_id}
            AND   action_id={action_id}
            AND   resource_id={resource_id}''')
        query.set_int('actor_id',    actor_id)
        query.set_int('action_id',   action_id)
        query.set_int('resource_id', resource_id)
        result = self.__db.execute(query.sql)
        assert result is not None
        row = result.shift()
        if row is None: return False
        return True


    def set_permission_from_id(self,
                               actor_list,
                               action_list,
                               resource_list,
                               permit):
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
        assert actor    is not None
        assert action   is not None
        assert resource is not None
        assert permit == True or permit == False
        return self.set_permission_from_id(actor.get_id(),
                                           action.get_id(),
                                           resource.get_id(),
                                           permit)


    def grant_from_id(self, actor_list, action_list, resource_list):
        assert actor_list    is not None
        assert action_list   is not None
        assert resource_list is not None
        return self.set_permission_from_id(actor_list,
                                           action_list,
                                           resource_list,
                                           True)


    def grant(self, actor, action, resource):
        assert actor    is not None
        assert action   is not None
        assert resource is not None
        return self.set_permission(actor, action, resource, True)


    def deny_from_id(self, actor_list, action_list, resource_list):
        assert actor_list    is not None
        assert action_list   is not None
        assert resource_list is not None
        return self.set_permission_from_id(actor_list,
                                           action_list,
                                           resource_list,
                                           False)


    def deny(self, actor, action, resource):
        assert actor    is not None
        assert action   is not None
        assert resource is not None
        return self.set_permission(actor, action, resource, False)
