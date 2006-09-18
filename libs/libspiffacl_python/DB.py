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
