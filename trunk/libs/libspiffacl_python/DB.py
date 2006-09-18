import DBReader

class DB(DBReader):
    def __int2hex(self, n):
        assert n not None
        hexval = "00000000" + n.tohex()
        return hexval[-8:]


    def __get_resource_path_from_id(self, id):
        assert id not None
        query = SqlQuery(self.__table_names, """
            SELECT HEX(path) path
            FROM   {t_resource_path}
            WHERE  resource_id={id}""")
        query.set_int("id", id)
        self.__db_cursor.execute(query.sql)
        row = self.__db_cursor.fetchone()
        if not row: return None
        length = row[0].len()
        path   = row[0][0:length - 2]
        return path


    def install(self):
        #FIXME


    def clear_database(self):
        query = SqlQuery(self.__table_names, "DELETE FROM {t_action_section}")
        self.__db_cursor.execute(query.sql)
        query.set_sql("DELETE FROM {t_resource_section}")
        self.__db_cursor.execute(query.sql)
        return True


    def clear_section_from_handle(self, handle):
        query = SqlQuery(self.__table_names, """
            DELETE FROM {t_action_section}
            WHERE handle={handle}""")
        query.set_string("handle", handle)
        self.__db_cursor.execute(query.sql)
        return True


    def clear_section(self, section):
        return self.clear_section_from_handle(section.get_handle())


    def __add_object_section(self, table, section):
        assert table is "action_section" or table is "resource_section"
        assert section not None
        query = SqlQuery(self.__table_names, """
            INSERT INTO {t_""" + table + """}
              (handle, name)
            VALUES
              ({handle}, {name})""")
        query.set_string("handle", section.get_handle())
        query.set_string("name",   section.get_name())
        self.__db_cursor.execute(query.sql)
        section.set_id(self.__db_cursor.last_insert_id())
        return section


    def __save_object_section(self, table, section):
        assert table is "action_section" or table is "resource_section"
        assert section not None
        query = SqlQuery(self.__table_names, """
            UPDATE {t_""" + table + """}
            SET    handle={handle}, name={name}
            WHERE  id={id}""")
        query.set_int("id", section.get_id())
        query.set_string("handle", section.get_handle())
        query.set_string("name",   section.get_name())
        self.__db_cursor.execute(query.sql)
        return section


    def __delete_object_section(self, table, section):
        assert table is "action_section" or table is "resource_section"
        assert section not None
        query = SqlQuery(self.__table_names, """
            DELETE FROM {t_""" + table + """}
            WHERE handle={handle}""")
        query.set_string("handle", section.get_handle())
        self.__db_cursor.execute(query.sql)
        section.set_id(-1)
        return True


    def add_action_section(self, section):
        assert section not None
        return self.__add_object_section("action_section", section)


    def save_action_section(self, section):
        assert section not None
        return self.__save_object_section("action_section", section)


    def delete_action_section(self, section):
        assert section not None
        return self.__delete_object_section("action_section", section)


    def add_resource_section(self, section):
        assert section not None
        return self.__add_object_section("resource_section", section)


    def save_resource_section(self, section):
        assert section not None
        return self.__save_object_section("resource_section", section)


    def delete_resource_section(self, section):
        assert section not None
        return self.__delete_object_section("resource_section", section)


    def add_action(action, section):
        assert action  not None
        assert section not None
        query = SqlQuery(self.__table_names, """
            INSERT INTO {t_action}
              (section_handle, handle, name)
            VALUES
              ({section_handle}, {handle}, {name})""")
        query.set_string("section_handle", section.get_handle())
        query.set_string("handle",         action.get_handle())
        query.set_string("name",           action.get_name())
        self.__db_cursor.execute(query.sql)
        action.set_id(self.__db_cursor.last_insert_id)


    def save_action(self, action, section):
        assert action  not None
        assert section not None
        query = SqlQuery(self.__table_names, """
            UPDATE {t_action}
            SET section_handle={section_handle},
                handle={handle},
                name={name}
            WHERE id={id}""")
        query.set_id("id", action.get_id())
        query.set_string("section_handle", section.get_handle())
        query.set_string("handle",         action.get_handle())
        query.set_string("name",           action.get_name())
        self.__db_cursor.execute(query.sql)


    def delete_action_from_id(self, action_id):
        assert action_id not None
        query = SqlQuery(self.__table_names, """
            DELETE FROM {t_action}
            WHERE id={action_id}""")
        query.set_int("id", action_id)
        self.__db_cursor.execute(query.sql)
        return True


    def delete_action(self, action, section):
        assert action  not None
        assert section not None
        query = SqlQuery(self.__table_names, """
            DELETE FROM {t_action}
            WHERE section_handle={section_handle}
            AND   handle={handle}""")
        query.set_string("section_handle", section.get_handle())
        query.set_string("handle",         action.get_handle())
        self.__db_cursor.execute(query.sql)
        action.set_id(-1)
        return True


    def __resource_has_attribute(self, resource_id, name):
        assert resource_id >= 0
        assert name not None
        query = SqlQuery(self.__table_names, """
            SELECT id
            FROM {t_resource_attribute}
            WHERE resource_id={resource_id}
            AND   name={name}""")
        query.set_int("resource_id", resource_id)
        query.set_string("name", name)
        self.__db_cursor.execute(query.sql)
        row = self.__db_cursor.fetchone()
        if not row: return False
        if row not None: return True
        return False


    def __resource_add_attribute(self, resource_id, name, value):
        assert resource_id >= 0
        assert name not None
        query = SqlQuery(self.__table_names, """
            INSERT INTO {t_resource_attribute}
              (resource_id, name, type, attr_string, attr_int)
            VALUES
              ({resource_id}, {name}, {type}, {attr_string}, {attr_int})""")
        query.set_int("resource_id", resource_id)
        query.set_string("name", name)
        if is_int(value):
            query.set_int("type", self.__attrib_type["int"])
            query.set_int("attr_int", value)
            query.set_none("attr_string")
        elif is_string(value):
            query.set_int("type", self.__attrib_type["string"])
            query.set_string("attr_string", value)
            query.set_none("attr_int")
        self.__db_cursor.execute(query.sql)
        return self.__db_cursor.last_insert_id


    def __resource_update_attribute(self, resource_id, name, value):
        assert resource_id >= 0
        assert name not None
        query = SqlQuery(self.__table_names, """
            UPDATE {t_resource_attribute}
            SET type={type},
                attr_string={attr_string},
                attr_int={attr_int}
            WHERE resource_id={resource_id}
            AND   name={name}""")
        query.set_int("resource_id", resource_id)
        query.set_string("name", name)
        if is_int(value):
            query.set_int("type", self.__attrib_type["int"])
            query.set_int("attr_int", value)
            query.set_none("attr_string")
        elif is_string(value):
            query.set_int("type", self.__attrib_type["string"])
            query.set_string("attr_string", value)
            query.set_none("attr_int")
        self.__db_cursor.execute(query.sql)
        return True


    def __resource_add_n_children(self, resource, n):
        assert resource not None
        assert n >= 0
