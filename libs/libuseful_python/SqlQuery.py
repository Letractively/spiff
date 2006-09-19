class SqlQuery:
    def __init__(self, table_names, sql):
        self.__tables_names = table_names
        self.__sql          = sql
        self.__data         = {}


    def set_sql(self, sql):
        self.__sql = sql
        for alias in self.__tables_names.keys():
            self.__sql.replace(alias, self.__tables_names[alias])


    def set_int(self, name, value):
        assert name is not None and name is not ''
        item = {'type': 'int', 'value': int(value)}
        self.__data[name] = item


    def set_string(self, name, value):
        assert name is not None and name is not ''
        item = {'type': 'string', 'value': value.escape()}
        self.__data[name] = item


    def set_hex(self, name, value):
        assert name is not None and name is not ''
        item = {'type': 'hex', 'value': '0x' + value}
        self.__data[name] = item


    def set_null(self, name):
        assert name is not None and name is not ''
        item = {'type': 'None', 'value': None}
        self.__data[name] = item


    def get_sql(self):
        for name in self.__data.keys():
            value = self.__data[name]['value'].replace('}', '\}')
            sql   = self.__sql.replace('{' + name + '}', value)
        return sql.replace('\}', '}')
