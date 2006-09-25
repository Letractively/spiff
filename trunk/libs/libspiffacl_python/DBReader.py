import sys
sys.path.append('..')

from ObjectSection   import *
from ActionSection   import *
from ResourceSection import *
from Acl             import *
from Action          import *
from Resource        import *
from ResourceGroup   import *
from Actor           import *
from ActorGroup      import *

from sqlalchemy                import *
from libuseful_python.SqlQuery import SqlQuery

class DBReader:
    fetch_all, fetch_groups, fetch_items = range(3)
    attrib_type_int, attrib_type_string = range(2)

    def __init__(self, db):
        self.db            = db
        self._table_prefix = ''
        self._table_names  = {}
        self._table_map    = {}
        self._table_list   = []
        self.__update_table_names()


    def __update_table_names(self):
        pfx   = self._table_prefix
        map   = self._table_map
        list  = self._table_list
        names = self._table_names
        names['t_action_section']     = pfx + 'action_section'
        names['t_resource_section']   = pfx + 'resource_section'
        names['t_action']             = pfx + 'action'
        names['t_resource']           = pfx + 'resource'
        names['t_resource_attribute'] = pfx + 'resource_attribute'
        names['t_resource_path']      = pfx + 'resource_path'
        names['t_path_ancestor_map']  = pfx + 'path_ancestor_map'
        names['t_acl']                = pfx + 'acl'
        metadata = BoundMetaData(self.db)
        list.append(Table(names['t_action_section'], metadata,
            Column('id',     Integer,     primary_key = True),
            Column('handle', String(230), unique = True),
            Column('name',   String(230), unique = True),
            mysql_engine='INNODB'
        ))
        map[list[-1].name] = list[-1]
        list.append(Table(names['t_resource_section'], metadata,
            Column('id',     Integer,     primary_key = True),
            Column('handle', String(230), unique = True),
            Column('name',   String(230), unique = True),
            mysql_engine='INNODB'
        ))
        map[list[-1].name] = list[-1]
        list.append(Table(names['t_action'], metadata,
            Column('id',             Integer,     primary_key = True),
            Column('section_handle', String(230), index = True),
            Column('handle',         String(230), unique = True),
            Column('name',           String(230), unique = True),
            ForeignKeyConstraint(['section_handle'],
                                 ['action_section.handle'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        map[list[-1].name] = list[-1]
        list.append(Table(names['t_resource'], metadata,
            Column('id',             Integer,     primary_key = True),
            Column('section_handle', String(230), index = True),
            Column('handle',         String(230), unique = True),
            Column('name',           String(230), unique = True),
            Column('is_actor',       Boolean,     index = True),
            Column('is_group',       Boolean,     index = True),
            ForeignKeyConstraint(['section_handle'],
                                 ['resource_section.handle'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        map[list[-1].name] = list[-1]
        list.append(Table(names['t_resource_attribute'], metadata,
            Column('id',             Integer,     primary_key = True),
            Column('resource_id',    Integer,     index = True),
            Column('name',           String(50)),
            Column('type',           Integer),
            Column('attr_string',    String(200)),
            Column('attr_int',       Integer),
            ForeignKeyConstraint(['resource_id'],
                                 ['resource.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        map[list[-1].name] = list[-1]
        list.append(Table(names['t_resource_path'], metadata,
            Column('id',             Integer,     primary_key = True),
            Column('path',           Binary(255), index = True),
            Column('depth',          Integer,     index = True),
            Column('resource_id',    Integer,     index = True),
            Column('n_children',     Integer),
            Column('refcount',       Integer),
            ForeignKeyConstraint(['resource_id'],
                                 ['resource.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        map[list[-1].name] = list[-1]
        list.append(Table(names['t_path_ancestor_map'], metadata,
            Column('resource_path',  Binary(255), index = True),
            Column('ancestor_path',  Binary(255), index = True),
            ForeignKeyConstraint(['resource_path'],
                                 ['resource_path.path'],
                                 ondelete = 'CASCADE'),
            ForeignKeyConstraint(['ancestor_path'],
                                 ['resource_path.path'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        map[list[-1].name] = list[-1]
        list.append(Table(names['t_acl'], metadata,
            Column('id',             Integer, primary_key = True),
            Column('actor_id',       Integer, index = True),
            Column('action_id',      Integer, index = True),
            Column('resource_id',    Integer, index = True),
            Column('permit',         Boolean, index = True),
            Column('refcount',       Integer),
            ForeignKeyConstraint(['actor_id'],
                                 ['resource_path.resource_id'],
                                 ondelete = 'CASCADE'),
            ForeignKeyConstraint(['action_id'],
                                 ['action.id'],
                                 ondelete = 'CASCADE'),
            ForeignKeyConstraint(['resource_id'],
                                 ['resource.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        map[list[-1].name] = list[-1]


    def debug(self, debug = True):
        self.db.debug = debug


    def set_table_prefix(self, prefix):
        self._table_prefix = prefix


    def __get_action_from_query(self, query):
        assert query is not None
        result = self.db.execute(query.get_sql())
        assert result is not None
        row = result.shift()
        if not row: return None
        action = Action(row['name'], row['handle'])
        action.set_id(row['id'])
        return action


    def get_action_from_id(self, id):
        assert id is not None
        query = SqlQuery(self._table_names, '''
            SELECT a.*
            FROM  {t_action} a
            WHERE a.id={id}''')
        query.set_int('id', id)
        return self.__get_action_from_query(query)


    def get_action_from_handle(self, handle, section_handle):
        assert handle         is not None
        assert section_handle is not None
        query = SqlQuery(self._table_names, '''
            SELECT a.*
            FROM  {t_action} a
            WHERE a.handle={handle}
            AND   a.section_handle={section_handle}''')
        query.set_string('handle',         handle)
        query.set_string('section_handle', section_handle)
        return self.__get_action_from_query(query)


    def __get_resource_from_row(self, row, type = None):
        if not row: return None
        if not type and row['is_actor']:
            type = 'Actor'
        elif not type and not row['is_actor']:
            type = 'Resource'
        if row['is_group']:
            type += 'Group'
        #print 'Type', type
        obj      = eval(type)
        resource = obj(row['name'], row['handle'])
        resource.set_id(row['id'])
        return resource


    def __get_resource_from_query(self, query, type = None):
        assert query is not None
        result = self.db.execute(query.get_sql())
        assert result is not None
        row = result.fetchone()
        if not row: return None
        resource = self.__get_resource_from_row(row, type)
        if not resource: return None

        # Append all attributes.
        while 1:
            # Determine attribute type.
            if row['type'] is self.attrib_type_int:
                value = int(row['attr_int'])
            elif row['type'] is self.attrib_type_string:
                value = row['string']

            # Append attribute.
            if row['attr_name'] is not None:
                resource.set_attribute(row['attr_name'], value)
            row = result.fetchone()
            if not row: break
            
        return resource


    def get_resource_from_id(self, id, type = None):
        assert id >= 0
        query = SqlQuery(self._table_names, '''
            SELECT r.*,a.name attr_name,a.type,a.attr_string,a.attr_int
            FROM      {t_resource}           r
            LEFT JOIN {t_resource_attribute} a ON r.id=a.resource_id
            WHERE r.id={id}''')
        query.set_int('id', id)
        return self.__get_resource_from_query(query, type)
        

    def get_resource_from_handle(self, handle, section_handle, type = None):
        assert handle         is not None
        assert section_handle is not None
        query = SqlQuery(self._table_names, '''
            SELECT r.*,a.name attr_name,a.type,a.attr_string,a.attr_int
            FROM      {t_resource}           r
            LEFT JOIN {t_resource_attribute} a ON r.id=a.resource_id
            WHERE r.handle={handle}
            AND   r.section_handle={section_handle}''')
        query.set_string('handle',         handle)
        query.set_string('section_handle', section_handle)
        return self.__get_resource_from_query(query, type)


    def get_resource_from_name(self, name, section_handle, type = None):
        assert name           is not None
        assert section_handle is not None
        query = SqlQuery(self._table_names, '''
            SELECT r.*,a.name attr_name,a.type,a.attr_string,a.attr_int
            FROM      {t_resource}           r
            LEFT JOIN {t_resource_attribute} a ON r.id=a.resource_id
            WHERE r.name={name}
            AND   r.section_handle={section_handle}''')
        query.set_string('name',           name)
        query.set_string('section_handle', section_handle)
        return self.__get_resource_from_query(query, type)


    def get_resource_children_from_id(self,
                                      resource_id,
                                      type = None,
                                      options = fetch_all):
        assert resource_id is not None

        # Define whether to fetch groups, items, or both.
        if options is fetch_groups:
            sql = ' AND r.is_group=1'
        elif options is fetch_items:
            sql = ' AND r.is_group=0'
        elif options is fetch_all:
            sql = ''
        else:
            assert False

        query = SqlQuery(self._table_names, '''
            SELECT r.*,a.name attr_name,a.type,a.attr_string,a.attr_int,t1.n_children
            FROM      {t_resource}           r
            LEFT JOIN {t_resource_attribute} a  ON r.id=a.resource_id
            LEFT JOIN {t_resource_path}      t1 ON t1.resource_id=r.id
            LEFT JOIN {t_path_ancestor_map}  p  ON t1.path=p.resource_path
            LEFT JOIN {t_resource_path}      t2 ON t2.path=p.ancestor_path
            WHERE t2.resource_id={resource_id}
            AND   t1.depth=t2.depth + 1''' + sql)
        query.set_int('resource_id', resource_id)
        result = self.db.execute(query.get_sql())
        assert result is not None

        # Collect all children.
        last     = None
        children = [];
        for row in result:
            if row['handle'] is not last:
                last = row['handle']
                resource = self.__get_resource_from_row(row, type)
                resource.set_n_children(row['n_children'])
                children.append(resource)

            # Append attribute (if any).
            if row['attr_name'] is None: continue
            if row['type'] is attrib_type_int:
                resource.set_attribute(row['name'], int(row['attr_int']))
            elif row['type'] is attrib_type_string:
                resource.set_attribute(row['name'], row['attr_string'])

        return children


    def get_resource_children(self,
                              resource,
                              type = None,
                              options = fetch_all):
        assert resource is not None
        if not resource.is_group(): return []
        resource_id = resource.get_id()
        return self.get_resource_children_from_id(resource_id, type, options)


    def get_resource_parents_from_id(self, parent_id, type = None):
        assert parent_id >= 0
        query = SqlQuery(self._table_names, '''
            SELECT r.*,a.name attr_name,a.type,a.attr_string,a.attr_int,t1.n_children
            FROM      {t_resource}           r
            LEFT JOIN {t_resource_attribute} a  ON r.id=a.resource_id
            LEFT JOIN {t_resource_path}      t1 ON t1.resource_id=r.id
            LEFT JOIN {t_path_ancestor_map}  p  ON t1.path=p.ancestor_path
            LEFT JOIN {t_resource_path}      t2 ON t2.path=p.resource_path
            WHERE t2.resource_id={resource_id}
            AND   t2.depth=t1.depth + 1''')
        query.set_int('resource_id', parent_id)
        result = self.db.execute(query.get_sql())
        assert result is not None

        # Collect all parents.
        last    = None
        parents = [];
        for row in result:
            if row['handle'] is not last:
                last = row['handle']
                resource = self.__get_resource_from_row(row, type)
                resource.set_n_children(row['n_children'])
                parents.append(resource)

            # Append attribute (if any).
            if row['attr_name'] is None: continue
            if row['type'] is attrib_type_int:
                resource.set_attribute(row['name'], int(row['attr_int']))
            elif row['type'] is attrib_type_string:
                resource.set_attribute(row['name'], row['attr_string'])

        return parents


    def get_resource_parents(self, resource, type = None):
        assert resource is not None
        return self.get_resource_parents_from_id(resource.get_id(), type)


    def has_permission_from_id(self, actor_id, action_id, resource_id):
        assert actor_id    is not None
        assert action_id   is not None
        assert resource_id is not None
        query = SqlQuery(self._table_names, '''
            SELECT    ac.permit
            FROM      {t_resource_path}     t1
            LEFT JOIN {t_path_ancestor_map} p1 ON t1.path=p1.resource_path
            LEFT JOIN {t_resource_path}     t2 ON t1.id=t2.id
                                               OR t2.path=p1.ancestor_path
            LEFT JOIN {t_acl}               ac ON t2.resource_id=ac.resource_id
            LEFT JOIN {t_resource_path}     t3 ON t3.id=ac.actor_id
            LEFT JOIN {t_path_ancestor_map} p2 ON t3.path=p2.ancestor_path
            LEFT JOIN {t_resource_path}     t4 ON t4.id=t3.id
                                               OR t4.path=p2.resource_path
            WHERE t1.resource_id={resource_id}
            AND   ac.action_id={action_id}
            AND   t4.resource_id={actor_id}
            ORDER BY t2.path, t3.path
            LIMIT    1''')
        query.set_int('actor_id',    actor_id)
        query.set_int('action_id',   action_id)
        query.set_int('resource_id', resource_id)
        result = self.db.execute(query.get_sql())
        assert result is not None
        row = result.shift()
        if row is None or row[0] is 0: return False
        return True


    def has_permission(self, actor, action, resource):
        assert actor    is not None
        assert action   is not None
        assert resource is not None
        actor_id    = actor.get_id()
        action_id   = action.get_id()
        resource_id = resource.get_id()
        return self.has_permission_from_id(actor_id, action_id, resource_id)


    def get_permission_list_from_id(self, actor_id, resource_id):
        assert actor_id    is not None
        assert resource_id is not None
        query = SqlQuery(self._table_names, '''
            SELECT    ac1.actor_id, ac1.resource_id, ac1.permit,
                      a.*,
                      s.id section_id, s.name section_name,
                      t2.depth, t3.depth,
                      max(t2.depth) t2_maxdepth, max(t3.depth) t3_maxdepth

            -- **************************************************************
            -- * 1. Get all ACLs that match the given resource.
            -- **************************************************************
            -- All paths that match directly.
            FROM resource_path t1

            -- All paths that are a parent of the direct match.
            LEFT JOIN path_ancestor_map p1 ON t1.path = p1.resource_path

            -- Still all paths that are a parent of the direct match, and also the
            -- direct match itself.
            LEFT JOIN resource_path t2 ON t1.id = t2.id OR t2.path = p1.ancestor_path

            -- All ACLs that reference the given resource or any of its parents.
            LEFT JOIN acl ac1 ON t2.resource_id = ac1.resource_id

            -- Path of the actor that is referenced by the ACL.
            LEFT JOIN resource_path t3 ON t3.id = ac1.actor_id

            -- Paths of all children of the actor.
            LEFT JOIN path_ancestor_map p2 ON t3.path = p2.ancestor_path

            -- Paths of all children of the actor, and also the actor itself.
            LEFT JOIN resource_path t4 ON t4.id = t3.id OR t4.path = p2.resource_path

            -- Informative only.
            LEFT JOIN action a ON a.id = ac1.action_id
            LEFT JOIN action_section s ON a.section_handle = s.handle
            

            -- **************************************************************
            -- * 2. We want to filter out any ACL that is defined for the
            -- * same action but has a shorter actor path.
            -- * A side effect of this way of doing it is that ACLs are 
            -- * added even if they were not defined for the right actor,
            -- * so we need to filter them out in the next step (see 3.).
            -- **************************************************************
            -- Get all ACLs that control the same action as the ACL above.
            LEFT JOIN acl ac2 ON ac1.action_id=ac2.action_id

            -- Get a list of all ACLs that perform the same action, but only
            -- if their actor path is longer.
            LEFT JOIN resource_path t5 ON ac2.actor_id=t5.resource_id AND t5.depth>t3.depth


            -- **************************************************************
            -- * 3. Filter out any ACL that is irrelevant because it does
            -- * not have the correct path.
            -- **************************************************************
            -- Get a list of all actors that are pointed to by the ACL joined
            -- above.
            LEFT JOIN resource_path t6 ON t6.resource_id=ac2.actor_id

            -- Get their children.
            LEFT JOIN path_ancestor_map p3 ON t6.path = p3.ancestor_path

            -- Keep only those that are inherited by the wanted actor.
            LEFT JOIN resource_path t7 ON p3.resource_path=t7.path OR t6.id=t7.id


            -- **************************************************************
            -- * 4. We want to filter out any ACL that is defined for the
            -- * same action but has a shorter resource path.
            -- * A side effect of this way of doing it is that ACLs are
            -- * added even if they were not defined for the right resource,
            -- * so we need to filter them out in the next step (see 3.).
            -- **************************************************************
            -- Get all ACLs that control the same action as the ACL above.
            LEFT JOIN acl ac3 ON ac1.action_id=ac3.action_id

            -- Get a list of all ACLs that perform the same action, but only
            -- if their resource path is longer.
            LEFT JOIN resource_path t8 ON ac3.resource_id=t8.resource_id AND t8.depth>t3.depth


            -- **************************************************************
            -- * 5. Filter out any ACL that is irrelevant because it does
            -- * not have the correct path.
            -- **************************************************************
            -- Get a list of all resources that are pointed to by the ACL
            -- joined above.
            LEFT JOIN resource_path t9 ON t9.resource_id=ac3.resource_id

            -- Get their children.
            LEFT JOIN path_ancestor_map p4 ON t9.path = p4.ancestor_path

            -- Keep only those that are inherited by the wanted resource.
            LEFT JOIN resource_path t10 ON p4.resource_path=t10.path OR t9.id=t10.id


            -- See 1.
            WHERE t1.resource_id={resource_id}
            AND   t4.resource_id={actor_id}

            -- See 2.
            AND t5.id IS NULL

            -- See 3.
            AND t7.resource_id={actor_id}

            -- See 4.
            AND t8.id IS NULL

            -- See 5.
            AND t10.resource_id={resource_id}

            -- Magic.
            GROUP BY t2.path, t3.path, ac1.action_id
            HAVING t2.depth = t2_maxdepth
            AND t3.depth = t3_maxdepth''')
        query.set_int('actor_id',    actor_id)
        query.set_int('resource_id', resource_id)
        result = self.db.execute(query.get_sql())
        assert result is not None

        # Collect all permissions.
        acl_list = [];
        for row in result:
            section = ActionSection(row['section_name'], row['section_handle'])
            action  = Action(row['name'], row['handle'], section)
            section.set_id(row['section_id'])
            action.set_id(row['id'])
            acl = Acl(row['actor_id'],
                      action,
                      row['resource_id'],
                      row['permit'])
            acl_list.append(acl)
        
        return acl_list


    def get_permission_list(self, actor, resource):
        assert actor    is not None
        assert resource is not None
        actor_id    = actor.get_id()
        resource_id = resource.get_id()
        return self.get_permission_list_from_id(actor_id, resource_id)


if __name__ == '__main__':
    import unittest
    import MySQLdb
    from sqlalchemy   import *
    from ConfigParser import RawConfigParser

    class DBReaderTest(unittest.TestCase):
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
            db   = create_engine(dbn)

            # We only test instantiation here, the other tests
            # are done in the derived class "DB".
            db = DBReader(db)
            assert db is not None

    testcase = DBReaderTest()
    runner   = unittest.TextTestRunner()
    runner.run(testcase)
