#from MySQLdb import escape_string

class SqlQuery:
    def __init__(self, table_names, sql):
        self.__tables_names = table_names
        self.__data         = {}
        self.set_sql(sql)


    def set_sql(self, sql):
        for alias in self.__tables_names.keys():
            sql = sql.replace('{' + alias + '}', self.__tables_names[alias])
        self.__sql = sql


    def set_int(self, name, value):
        assert name is not None and name is not ''
        item = {'type': 'int', 'value': repr(int(value))}
        self.__data[name] = item


    def set_string(self, name, value):
        assert name is not None and name is not ''
        #item = {'type': 'string', 'value': escape_string(value)}
        value = value.replace('\'', '\'\'')
        item  = {'type': 'string', 'value': "'" + value + "'"}
        self.__data[name] = item


    def set_hex(self, name, value):
        assert name is not None and name is not ''
        value = value.replace('\'', '\'\'')
        item  = {'type': 'hex', 'value': '0x' + value}
        self.__data[name] = item


    def set_null(self, name):
        assert name is not None and name is not ''
        item = {'type': 'None', 'value': 'NULL'}
        self.__data[name] = item


    def get_sql(self):
        sql = self.__sql
        for name in self.__data.keys():
            value = self.__data[name]['value']
            value = value.replace('}', '\}')
            sql   = sql.replace('{' + name + '}', value)
        return sql.replace('\}', '}')


if __name__ == '__main__':
    import unittest

    class SqlQueryTest(unittest.TestCase):
        def runTest(self):
            # Read config.
            tbl    = {'my_tbl': 'my_table'}
            sql_in = '''
                SELECT * FROM {my_tbl}
                WHERE id={id}
                AND   string={string}
                AND   hex={hex}
                AND   null={null}'''
            sql_out = '''
                SELECT * FROM my_table
                WHERE id=1
                AND   string='my_string'
                AND   hex=0x0f
                AND   null=NULL'''
            query = SqlQuery(tbl, sql_in)
            query.set_int('id', 1)
            query.set_string('string', 'my_string')
            query.set_hex('hex', '0f')
            query.set_null('null')
            print query.get_sql()
            assert query.get_sql() != sql_in
            assert query.get_sql() == sql_out

    testcase = SqlQueryTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
