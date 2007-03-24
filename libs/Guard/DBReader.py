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
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from sqlalchemy import *
from functions  import bin_path2list

from ObjectSection   import *
from ActionSection   import *
from ResourceSection import *
from Acl             import *
from Action          import *
from Resource        import *
from ResourceGroup   import *
from ResourcePath    import *
from Actor           import *
from ActorGroup      import *


class DBReader:
    fetch_all, fetch_groups, fetch_items = range(3)
    attrib_type_int, attrib_type_bool, attrib_type_string = range(3)

    def __init__(self, db):
        """
        Instantiates a new DBReader.
        
        @type  db: object
        @param db: An sqlalchemy database connection.
        @rtype:  DB
        @return: The new instance.
        """
        self.db            = db
        self.db_metadata   = BoundMetaData(self.db)
        self._table_prefix = 'guard_'
        self._table_map    = {}
        self._table_list   = []
        self.__update_table_names()


    def __add_table(self, table):
        """
        Adds a new table to the internal table list.
        
        @type  table: Table
        @param table: An sqlalchemy table.
        """
        pfx = self._table_prefix
        self._table_list.append(table)
        self._table_map[table.name[len(pfx):]] = table


    def __update_table_names(self):
        """
        Adds all tables to the internal table list.
        """
        pfx = self._table_prefix
        self._table_list = []
        self.__add_table(Table(pfx + 'action_section', self.db_metadata,
            Column('id',     Integer,     primary_key = True),
            Column('handle', String(230), unique = True),
            Column('name',   String(230), unique = True),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'resource_section', self.db_metadata,
            Column('id',     Integer,     primary_key = True),
            Column('handle', String(230), unique = True),
            Column('name',   String(230), unique = True),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'action', self.db_metadata,
            Column('id',             Integer,     primary_key = True),
            Column('section_handle', String(230), index = True),
            Column('handle',         String(230)),
            Column('name',           String(230), unique = True),
            ForeignKeyConstraint(['section_handle'],
                                 [pfx + 'action_section.handle'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        #FIXME: Figure out how to create a unique key over multiple columns
        # and add one over section_handle+handle and section_handle+name.
        self.__add_table(Table(pfx + 'resource', self.db_metadata,
            Column('id',             Integer,     primary_key = True),
            Column('section_handle', String(230), index = True),
            Column('handle',         String(230)),
            Column('name',           String(230)),
            Column('n_children',     Integer,     index = True, default = 0),
            Column('is_actor',       Boolean,     index = True),
            Column('is_group',       Boolean,     index = True),
            ForeignKeyConstraint(['section_handle'],
                                 [pfx + 'resource_section.handle'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'resource_attribute', self.db_metadata,
            Column('id',             Integer,     primary_key = True),
            Column('resource_id',    Integer,     index = True),
            Column('name',           String(50)),
            Column('type',           Integer),
            Column('attr_string',    String(200)),
            Column('attr_int',       Integer),
            ForeignKeyConstraint(['resource_id'],
                                 [pfx + 'resource.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'resource_path', self.db_metadata,
            Column('id',             Integer,     primary_key = True),
            Column('path',           Binary(255), index = True),
            Column('depth',          Integer,     index = True),
            Column('resource_id',    Integer,     index = True),
            Column('refcount',       Integer,     index = True, default = 0),
            ForeignKeyConstraint(['resource_id'],
                                 [pfx + 'resource.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'path_ancestor_map', self.db_metadata,
            Column('resource_path_id',  Integer, index = True),
            Column('ancestor_path_id',  Integer, index = True),
            ForeignKeyConstraint(['resource_path_id'],
                                 [pfx + 'resource_path.id'],
                                 ondelete = 'CASCADE'),
            ForeignKeyConstraint(['ancestor_path_id'],
                                 [pfx + 'resource_path.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'acl', self.db_metadata,
            Column('id',             Integer, primary_key = True),
            Column('actor_id',       Integer, index = True),
            Column('action_id',      Integer, index = True),
            Column('resource_id',    Integer, index = True),
            Column('permit',         Boolean, index = True),
            Column('refcount',       Integer),
            ForeignKeyConstraint(['actor_id'],
                                 [pfx + 'resource.id'],
                                 ondelete = 'CASCADE'),
            ForeignKeyConstraint(['action_id'],
                                 [pfx + 'action.id'],
                                 ondelete = 'CASCADE'),
            ForeignKeyConstraint(['resource_id'],
                                 [pfx + 'resource.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))


    def debug(self, debug = True):
        """
        Enable/disable debugging.

        @type  debug: Boolean
        @param debug: True to enable debugging.
        """
        self.db.debug = debug


    def set_table_prefix(self, prefix):
        """
        Define a table prefix. Default is 'warehouse_'.

        @type  prefix: string
        @param prefix: The new prefix.
        """
        self._table_prefix = prefix
        self.__update_table_names()


    def get_table_prefix(self):
        """
        Returns the current database table prefix.
        
        @rtype:  string
        @return: The current prefix.
        """
        return self._table_prefix


    def __get_action_from_query(self, query):
        assert query is not None
        result = query.execute()
        assert result is not None
        row = result.fetchone()
        if not row: return None
        action = Action(row['name'], row['handle'])
        action.set_id(row['id'])
        return action


    def get_action_from_id(self, id):
        assert id is not None
        table  = self._table_map['action']
        select = table.select(table.c.id == id)
        return self.__get_action_from_query(select)


    def get_action_from_handle(self, handle, section_handle):
        assert handle         is not None
        assert section_handle is not None
        table  = self._table_map['action']
        select = table.select(and_(table.c.handle         == handle,
                                   table.c.section_handle == section_handle))
        return self.__get_action_from_query(select)


    def __get_resource_from_row(self, row, type = None):
        if not row: return None
        tbl_r = self._table_map['resource']
        if not type:
            if row[tbl_r.c.is_actor] and row[tbl_r.c.is_group]:
                type = ActorGroup
            elif row[tbl_r.c.is_actor]:
                type = Actor
            elif row[tbl_r.c.is_group]:
                type = ResourceGroup
            else:
                type = Resource
        #print "Type:", type
        resource = type(row[tbl_r.c.name], row[tbl_r.c.handle])
        resource.set_id(row[tbl_r.c.id])
        resource.set_n_children(row[tbl_r.c.n_children])
        return resource


    def __get_resource_from_query(self, query, type = None, always_list = False):
        """
        May return a resource list, a single resource, or None.
        If always_list is True, a list is returned even if only a single
        result was produced.
        """
        assert query is not None
        result = query.execute()
        assert result is not None
        row = result.fetchone()
        if not row: return None

        tbl_r         = self._table_map['resource']
        tbl_a         = self._table_map['resource_attribute']
        last_id       = None
        resource_list = []
        while row is not None:
            last_id  = row[tbl_r.c.id]
            resource = self.__get_resource_from_row(row, type)
            resource_list.append(resource)
            if not resource: break

            # Append all attributes.
            while 1:
                # Determine attribute type.
                if row[tbl_a.c.type] == self.attrib_type_int:
                    value = int(row[tbl_a.c.attr_int])
                elif row[tbl_a.c.type] == self.attrib_type_bool:
                    value = bool(row[tbl_a.c.attr_int])
                elif row[tbl_a.c.type] == self.attrib_type_string:
                    value = row[tbl_a.c.attr_string]

                # Append attribute.
                if row[tbl_a.c.type] is not None:
                    resource.set_attribute(row[tbl_a.c.name], value)
                row = result.fetchone()

                if not row: break
                if last_id != row[tbl_r.c.id]:
                    break

        if always_list:
            return resource_list
        if len(resource_list) == 1:
            return resource
        return resource_list


    def get_resource_from_id(self, id, type = None):
        assert id >= 0
        tbl_r  = self._table_map['resource']
        tbl_a  = self._table_map['resource_attribute']
        table  = outerjoin(tbl_r, tbl_a, tbl_r.c.id == tbl_a.c.resource_id)
        select = table.select(tbl_r.c.id == id, use_labels = True)
        return self.__get_resource_from_query(select, type)


    def get_resource_from_handle(self, handle, section_handle, type = None):
        assert handle         is not None
        assert section_handle is not None
        tbl_r  = self._table_map['resource']
        tbl_a  = self._table_map['resource_attribute']
        table  = outerjoin(tbl_r, tbl_a, tbl_r.c.id == tbl_a.c.resource_id)
        select = table.select(and_(tbl_r.c.handle         == handle,
                                   tbl_r.c.section_handle == section_handle),
                              use_labels = True)
        return self.__get_resource_from_query(select, type)


    def get_resource_from_name(self, name, section_handle, type = None):
        assert name           is not None
        assert section_handle is not None
        tbl_r  = self._table_map['resource']
        tbl_a  = self._table_map['resource_attribute']
        table  = outerjoin(tbl_r, tbl_a, tbl_r.c.id == tbl_a.c.resource_id)
        select = table.select(and_(tbl_r.c.name           == name,
                                   tbl_r.c.section_handle == section_handle),
                              use_labels = True)
        return self.__get_resource_from_query(select, type)


    def get_resource_list(self,
                          section_handle = None,
                          offset         = 0,
                          limit          = 0,
                          type           = None,
                          options        = fetch_all):
        """
        Returns a list of resources out of the given section. If section_handle
        is None, all resources are returned.
        """
        tbl_r  = self._table_map['resource']
        tbl_a  = self._table_map['resource_attribute']
        table  = outerjoin(tbl_r, tbl_a, tbl_r.c.id == tbl_a.c.resource_id)
        where  = None

        if section_handle is not None:
            where = and_(where, tbl_r.c.section_handle == section_handle)
        
        # Define whether to fetch groups, items, or both.
        if options is self.fetch_groups:
            where = and_(where, tbl_r.c.is_group == True)
        elif options is self.fetch_items:
            where = and_(where, tbl_r.c.is_group == False)
        elif options is self.fetch_all:
            pass
        else:
            assert False # Unknown option.

        select = table.select(where,
                              use_labels = True,
                              limit      = limit,
                              offset     = offset)
        return self.__get_resource_from_query(select, type, True)


    def get_resource_list_from_id_list(self, id_list, type = None):
        assert id_list is not None
        if len(id_list) == 0: return []
        tbl_r  = self._table_map['resource']
        tbl_a  = self._table_map['resource_attribute']
        table  = outerjoin(tbl_r, tbl_a, tbl_r.c.id == tbl_a.c.resource_id)
        where_clause = None
        for id in id_list:
            if where_clause is None:
                where_clause = (tbl_r.c.id == id)
            else:
                where_clause = or_(where_clause, tbl_r.c.id == id)
        if where_clause is None:
            select = table.select(use_labels = True)
        else:
            select = table.select(where_clause, use_labels = True)
        return self.__get_resource_from_query(select, type, True)
        

    def get_resource_list_from_attribute(self, name, value, r_type = None):
        assert name  is not None
        assert value is not None
        tbl_a  = self._table_map['resource_attribute']
        tbl_r  = self._table_map['resource']
        table  = outerjoin(tbl_a, tbl_r, tbl_r.c.id == tbl_a.c.resource_id)
        if type(value) == type(0):
            attr_type = self.attrib_type_int
            select = table.select(and_(tbl_a.c.name        == name,
                                       tbl_a.c.type        == attr_type,
                                       tbl_a.c.attr_int    == int(value)),
                                  use_labels = True)
        elif type(value) == type(True):
            attr_type = self.attrib_type_bool
            select = table.select(and_(tbl_a.c.name        == name,
                                       tbl_a.c.type        == attr_type,
                                       tbl_a.c.attr_int    == int(value)),
                                  use_labels = True)
        elif type(value) == type(''):
            attr_type = self.attrib_type_string
            select = table.select(and_(tbl_a.c.name        == name,
                                       tbl_a.c.type        == attr_type,
                                       tbl_a.c.attr_string == value),
                                  use_labels = True)
        else:
            assert False # Unknown attribute type.
        return self.__get_resource_from_query(select, r_type, True)


    def get_resource_children_from_id(self,
                                      resource_id,
                                      type = None,
                                      options = fetch_all):
        assert resource_id is not None

        tbl_r  = self._table_map['resource']
        tbl_a  = self._table_map['resource_attribute']
        tbl_p1 = self._table_map['resource_path'].alias('p1')
        tbl_m  = self._table_map['path_ancestor_map']
        tbl_p2 = self._table_map['resource_path'].alias('p2')
        table  = tbl_r.outerjoin(tbl_a,  tbl_r.c.id  == tbl_a.c.resource_id)
        table  = table.outerjoin(tbl_p1, tbl_r.c.id  == tbl_p1.c.resource_id)
        table  = table.outerjoin(tbl_m,  tbl_p1.c.id == tbl_m.c.resource_path_id)
        table  = table.outerjoin(tbl_p2, tbl_p2.c.id == tbl_m.c.ancestor_path_id)
        select = table.select(and_(tbl_p2.c.resource_id == resource_id,
                                   tbl_p1.c.depth       == tbl_p2.c.depth + 1),
                              order_by   = [tbl_p1.c.resource_id],
                              use_labels = True)

        # Define whether to fetch groups, items, or both.
        if options is self.fetch_groups:
            result = select.execute(is_group = True)
        elif options is self.fetch_items:
            result = select.execute(is_group = False)
        elif options is self.fetch_all:
            result = select.execute()
        else:
            assert False

        assert result is not None

        # Collect all children.
        last     = None
        children = [];
        for row in result:
            if row[tbl_p1.c.resource_id] != last:
                last = row[tbl_p1.c.resource_id]
                resource = self.__get_resource_from_row(row, type)
                resource.set_n_children(row[tbl_r.c.n_children])
                children.append(resource)

            # Append attribute (if any).
            if row[tbl_a.c.name] is None: continue
            if row[tbl_a.c.type] == self.attrib_type_int:
                resource.set_attribute(row[tbl_a.c.name],
                                       int(row[tbl_a.c.attr_int]))
            elif row[tbl_a.c.type] == self.attrib_type_bool:
                resource.set_attribute(row[tbl_a.c.name],
                                       bool(row[tbl_a.c.attr_int]))
            elif row[tbl_a.c.type] == self.attrib_type_string:
                resource.set_attribute(row[tbl_a.c.name],
                                       row[tbl_a.c.attr_string])

        return children


    def get_resource_path_from_id(self, id):
        assert id >= 0
        tbl_p  = self._table_map['resource_path']
        select = tbl_p.select(tbl_p.c.resource_id == id)
        result = select.execute()
        assert result is not None
        row = result.fetchone()
        assert row is not None
        list = bin_path2list(row[tbl_p.c.path])
        return ResourcePath(list)


    def get_resource_children(self,
                              resource,
                              type = None,
                              options = fetch_all):
        assert resource is not None
        if not resource.is_group(): return []
        resource_id = resource.get_id()
        return self.get_resource_children_from_id(resource_id, type, options)


    def get_resource_parents_from_id(self, child_id, type = None):
        assert child_id is not None

        tbl_r  = self._table_map['resource']
        tbl_a  = self._table_map['resource_attribute']
        tbl_p1 = self._table_map['resource_path'].alias('p1')
        tbl_m  = self._table_map['path_ancestor_map']
        tbl_p2 = self._table_map['resource_path'].alias('p2')
        table  = tbl_r.outerjoin(tbl_a,  tbl_r.c.id  == tbl_a.c.resource_id)
        table  = table.outerjoin(tbl_p1, tbl_r.c.id  == tbl_p1.c.resource_id)
        table  = table.outerjoin(tbl_m,  tbl_p1.c.id == tbl_m.c.ancestor_path_id)
        table  = table.outerjoin(tbl_p2, tbl_p2.c.id == tbl_m.c.resource_path_id)
        select = table.select(and_(tbl_p2.c.resource_id == child_id,
                                   tbl_p2.c.depth       == tbl_p1.c.depth + 1),
                              order_by   = [tbl_p1.c.resource_id],
                              use_labels = True)
        result = select.execute()
        assert result is not None

        # Collect all parents.
        last    = None
        parents = [];
        for row in result:
            if row[tbl_p1.c.resource_id] != last:
                last = row[tbl_p1.c.resource_id]
                resource = self.__get_resource_from_row(row, type)
                resource.set_n_children(row[tbl_r.c.n_children])
                parents.append(resource)

            # Append attribute (if any).
            if row[tbl_a.c.name] is None: continue
            if row[tbl_a.c.type] == self.attrib_type_int:
                resource.set_attribute(row[tbl_a.c.name],
                                       int(row[tbl_a.c.attr_int]))
            elif row[tbl_a.c.type] == self.attrib_type_bool:
                resource.set_attribute(row[tbl_a.c.name],
                                       bool(row[tbl_a.c.attr_string]))
            elif row[tbl_a.c.type] == self.attrib_type_string:
                resource.set_attribute(row[tbl_a.c.name],
                                       row[tbl_a.c.attr_string])

        return parents


    def get_resource_parents(self, resource, type = None):
        assert resource is not None
        return self.get_resource_parents_from_id(resource.get_id(), type)


    def has_permission_from_id(self, actor_id, action_id, resource_id):
        assert actor_id    is not None
        assert action_id   is not None
        assert resource_id is not None
        tbl_p1 = self._table_map['resource_path'].alias('p1')
        tbl_m1 = self._table_map['path_ancestor_map'].alias('m1')
        tbl_p2 = self._table_map['resource_path'].alias('p2')
        tbl_ac = self._table_map['acl']
        tbl_p3 = self._table_map['resource_path'].alias('p3')
        tbl_m2 = self._table_map['path_ancestor_map'].alias('m2')
        tbl_p4 = self._table_map['resource_path'].alias('p4')
        tbl = tbl_p1.outerjoin(tbl_m1, tbl_p1.c.id == tbl_m1.c.resource_path_id)
        tbl = tbl.outerjoin(tbl_p2, or_(tbl_p2.c.id == tbl_p1.c.id,
                                        tbl_p2.c.id == tbl_m1.c.ancestor_path_id))
        tbl = tbl.outerjoin(tbl_ac, tbl_p2.c.resource_id == tbl_ac.c.resource_id)
        tbl = tbl.outerjoin(tbl_p3, tbl_p3.c.id == tbl_ac.c.actor_id)
        tbl = tbl.outerjoin(tbl_m2, tbl_p3.c.id == tbl_m2.c.ancestor_path_id)
        tbl = tbl.outerjoin(tbl_p4, or_(tbl_p4.c.id == tbl_p3.c.id,
                                        tbl_p4.c.id == tbl_m2.c.resource_path_id))
        sel = select([tbl_ac.c.permit],
                     and_(tbl_p1.c.resource_id == resource_id,
                          tbl_ac.c.action_id   == action_id,
                          tbl_p4.c.resource_id == actor_id),
                     order_by   = [desc(tbl_p2.c.path), desc(tbl_p3.c.path)],
                     use_labels = True,
                     from_obj   = [tbl])

        result = sel.execute()
        assert result is not None
        row = result.fetchone()
        #print "Searching: (%i, %i, %i)", (actor_id, action_id, resource_id)
        if row is None: return False
        return row[0]


    def has_permission(self, actor, action, resource):
        assert actor    is not None
        assert action   is not None
        assert resource is not None
        actor_id    = actor.get_id()
        action_id   = action.get_id()
        resource_id = resource.get_id()
        return self.has_permission_from_id(actor_id, action_id, resource_id)


    def get_permission_list_from_id(self, actor_id, *args, **kwargs):
        """
        Returns a list of ACLs that match the given criteria. The function
        ignores inheritance, so that ACLs are only returned if they were
        defined specificly for the requested resource.
        
        Allowed argument keywords include: action_id, resource_id,
        permit, action_section_handle and resource_section_handle.
        All arguments are optional; if no arguments are given all ACLs for
        the given actor_id are returned.
        """
        # Get a list of all resources.
        tbl_p1 = self._table_map['resource_path'].alias('p1')

        # Search all ACLs that are defined for those resources.
        tbl_ac = self._table_map['acl']
        tbl = tbl_p1.outerjoin(tbl_ac, tbl_p1.c.resource_id == tbl_ac.c.resource_id)

        # Now search the corresponding actors.
        tbl_p3 = self._table_map['resource_path'].alias('p3')
        tbl = tbl.outerjoin(tbl_p3, tbl_p3.c.id == tbl_ac.c.actor_id)
        where = tbl_p3.c.resource_id == actor_id

        # Informative only.
        tbl_a1 = self._table_map['action'].alias('a1')
        tbl = tbl.outerjoin(tbl_a1, tbl_a1.c.id == tbl_ac.c.action_id)

        if kwargs.has_key('action_id'):
            where = and_(where, tbl_ac.c.action_id == kwargs['action_id'])

        if kwargs.has_key('resource_id'):
            where = and_(where, tbl_p1.c.resource_id == kwargs['resource_id'])

        if kwargs.has_key('permit'):
            where = and_(where, tbl_ac.c.permit == kwargs['permit'])

        if kwargs.has_key('action_section_handle'):
            handle = kwargs['action_section_handle']
            where  = and_(where, tbl_a1.c.section_handle == handle)

        if kwargs.has_key('resource_section_handle'):
            tbl_r1 = self._table_map['resource'].alias('r1')
            tbl    = tbl.outerjoin(tbl_r1, tbl_r1.c.id == tbl_ac.c.resource_id)
            handle = kwargs['resource_section_handle']
            where  = and_(where, tbl_r1.c.section_handle == handle)

        sel = select([tbl_ac.c.id,
                      tbl_ac.c.actor_id,
                      tbl_ac.c.resource_id,
                      tbl_ac.c.permit,
                      tbl_a1.c.id,
                      tbl_a1.c.name,
                      tbl_a1.c.handle],
                     where,
                     order_by   = [desc(tbl_p3.c.path), desc(tbl_p1.c.path)],
                     use_labels = True,
                     from_obj   = [tbl])

        result = sel.execute()
        assert result is not None

        # Collect all permissions.
        acl_list = [];
        for row in result:
            action = Action(row[tbl_a1.c.name], row[tbl_a1.c.handle])
            action.set_id(row[tbl_a1.c.id])
            acl = Acl(row[tbl_ac.c.actor_id],
                      action,
                      row[tbl_ac.c.resource_id],
                      row[tbl_ac.c.permit])
            acl.set_id(row[tbl_ac.c.id])
            acl_list.append(acl)

        return acl_list


    def get_permission_list_from_id_with_inheritance(self, *args, **kwargs):
        """
        Returns a list of ACLs that match the given criteria. The function
        honors inheritance, so that ACLs are returned even if they were
        defined for a parent of the requested resource.

        This function is expensive and should be used with care.
        You might want to consider using get_permission_list_from_id()
        instead.
        
        Allowed argument keywords include: actor_id, action_id, resource_id,
        permit, actor_section_handle, action_section_handle and
        resource_section_handle.
        All arguments are optional; if no arguments are given all ACLs are
        returned.
        """
        # Looking to find a bug in this function? Congratulations, you are
        # about to enter hell.
        # Also, if you find (and fix) that damn bug here, you are totally a
        # hero - even I have difficulty understanding how the hell I managed
        # to write that. But don't blame me, because any database design
        # will suck in at least one respect when you implement ACLs.
        where = None

        # Get all actor paths.
        tbl_p1 = self._table_map['resource_path'].alias('p1')
        if kwargs.has_key('actor_id'):
            actor_id = kwargs['actor_id']
            where    = and_(where, tbl_p1.c.resource_id == actor_id)

        # All paths that are a parent of the path.
        tbl_m1 = self._table_map['path_ancestor_map'].alias('m1')
        tbl = tbl_p1.outerjoin(tbl_m1, tbl_p1.c.id == tbl_m1.c.resource_path_id)

        # Still all paths that are a child of the direct match, and also the
        # direct match itself.
        tbl_p2 = self._table_map['resource_path'].alias('p2')
        tbl = tbl.outerjoin(tbl_p2, or_(tbl_p2.c.id == tbl_p1.c.id,
                                        tbl_p2.c.id == tbl_m1.c.ancestor_path_id))

        # All ACLs that reference the given actor or any of its parents.
        tbl_ac1 = self._table_map['acl'].alias('ac1')
        tbl = tbl.outerjoin(tbl_ac1, tbl_p2.c.resource_id == tbl_ac1.c.actor_id)
        if kwargs.has_key('permit'):
            permit = kwargs['permit']
            where  = and_(where, tbl_ac1.c.permit == permit)

        # Path of the resource that is referenced by the ACL.
        tbl_p3 = self._table_map['resource_path'].alias('p3')
        tbl = tbl.outerjoin(tbl_p3, tbl_p3.c.resource_id == tbl_ac1.c.resource_id)
        if kwargs.has_key('resource_id'):
            resource_id = kwargs['resource_id']
            where       = and_(where, tbl_p3.c.resource_id == resource_id)

        # Paths of all children of the resource.
        tbl_m2 = self._table_map['path_ancestor_map'].alias('m2')
        tbl = tbl.outerjoin(tbl_m2, tbl_p3.c.id == tbl_m2.c.ancestor_path_id)

        # Paths of all children of the resource, and also the resource itself.
        tbl_p4 = self._table_map['resource_path'].alias('p4')
        tbl = tbl.outerjoin(tbl_p4, or_(tbl_p4.c.id == tbl_p3.c.id,
                                        tbl_p4.c.id == tbl_m2.c.resource_path_id))

        # Informative only.
        tbl_a1 = self._table_map['action'].alias('a1')
        tbl = tbl.outerjoin(tbl_a1, tbl_a1.c.id == tbl_ac1.c.action_id)
        if kwargs.has_key('action_id'):
            action_id = kwargs['action_id']
            where     = and_(where, tbl_a1.c.id == action_id)
        if kwargs.has_key('action_section_handle'):
            handle = kwargs['action_section_handle']
            where  = and_(where, tbl_a1.c.section_handle == handle)

        # Informative only.
        tbl_s1 = self._table_map['action_section'].alias('s1')
        tbl = tbl.outerjoin(tbl_s1, tbl_a1.c.section_handle == tbl_s1.c.handle)
        
        # Informative only.
        if kwargs.has_key('resource_section_handle'):
            handle = kwargs['resource_section_handle']
            tbl_r1 = self._table_map['resource'].alias('r1')
            tbl    = tbl.outerjoin(tbl_r1, tbl_r1.c.id == tbl_p4.c.resource_id)
            where  = and_(where, tbl_r1.c.section_handle == handle)

        # Informative only.
        if kwargs.has_key('actor_section_handle'):
            handle = kwargs['actor_section_handle']
            tbl_r2 = self._table_map['resource'].alias('r2')
            tbl    = tbl.outerjoin(tbl_r2, tbl_r2.c.id == tbl_p2.c.resource_id)
            where  = and_(where, tbl_r2.c.section_handle == handle)

        # Get all ACLs that control the same resource/action as the ACL above.
        tbl_ac2 = self._table_map['acl'].alias('ac2')
        tbl = tbl.outerjoin(tbl_ac2, and_(tbl_ac1.c.action_id   == tbl_ac2.c.action_id,
                                          tbl_ac1.c.resource_id == tbl_ac2.c.resource_id))
        
        # Get a list of all the actors that perform the action.
        tbl_p5 = self._table_map['resource_path'].alias('p5')
        tbl = tbl.outerjoin(tbl_p5, tbl_ac2.c.actor_id == tbl_p5.c.resource_id)

        # Make sure that the actor is a parent of the wanted one.
        tbl_m3 = self._table_map['path_ancestor_map'].alias('m3')
        tbl = tbl.outerjoin(tbl_m3, tbl_p5.c.id == tbl_m3.c.ancestor_path_id)
        
        # Get the list of all the children.
        tbl_p6 = self._table_map['resource_path'].alias('p6')
        tbl = tbl.outerjoin(tbl_p6, or_(tbl_m3.c.resource_path_id == tbl_p6.c.id,
                                        tbl_p5.c.id               == tbl_p6.c.id))
        if kwargs.has_key('actor_id'):
            actor_id = kwargs['actor_id']
            where = and_(where, tbl_p6.c.resource_id == actor_id)

        group_by = [tbl_ac1.c.actor_id, tbl_ac1.c.action_id, tbl_ac1.c.resource_id]
        sel = select([tbl_ac1.c.id,
                      tbl_ac1.c.actor_id,
                      tbl_ac1.c.resource_id,
                      tbl_ac1.c.permit,
                      tbl_a1,
                      tbl_s1.c.id,
                      tbl_s1.c.handle,
                      tbl_s1.c.name,
                      tbl_p1.c.resource_id,
                      tbl_p2.c.depth.label('p2_depth'),
                      func.max(tbl_p5.c.depth).label('p5_max_depth')],
                     where,
                     from_obj   = [tbl],
                     use_labels = True,
                     group_by   = group_by,
                     having     = 'p2_depth = p5_max_depth',
                     order_by   = [tbl_p2.c.path, tbl_p4.c.path])

        #print sel
        result = sel.execute()
        assert result is not None

        # Collect all permissions.
        acl_list = []
        for row in result:
            #print row
            action = Action(row[tbl_a1.c.name], row[tbl_a1.c.handle])
            action.set_id(row[tbl_a1.c.id])
            acl = Acl(row[tbl_ac1.c.actor_id],
                      action,
                      row[tbl_ac1.c.resource_id],
                      row[tbl_ac1.c.permit],
                      row[tbl_p1.c.resource_id] != row[tbl_ac1.c.actor_id])
            acl.set_id(row[tbl_ac1.c.id])
            acl_list.append(acl)
        
        #print "LENGTH:", len(acl_list)
        return acl_list


    def get_permission_list_with_inheritance(self, *args, **kwargs):
        """
        Returns a list of ACLs that match the given criteria. Allowed argument
        keywords include: actor, action, resource, permit, actor_section,
        action_section and resource_section.
        All arguments are optional.
        """
        if kwargs.has_key('actor'):
            kwargs['actor_id'] = kwargs['actor'].get_id()

        if kwargs.has_key('action'):
            kwargs['action_id'] = kwargs['action'].get_id()

        if kwargs.has_key('resource'):
            kwargs['resource_id'] = kwargs['resource'].get_id()

        if kwargs.has_key('actor_section'):
            handle = kwargs['actor_section'].get_handle()
            kwargs['actor_section_handle'] = handle

        if kwargs.has_key('action_section'):
            handle = kwargs['action_section'].get_handle()
            kwargs['action_section_handle'] = handle

        if kwargs.has_key('resource_section'):
            handle = kwargs['resource_section'].get_handle()
            kwargs['resource_section_handle'] = handle

        return self.get_permission_list_from_id_with_inheritance(**kwargs)


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
