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

from ObjectSection   import *
from ActionSection   import *
from ResourceSection import *
from Acl             import *
from Action          import *
from Resource        import *
from ResourceGroup   import *
from Actor           import *
from ActorGroup      import *


class DBReader:
    fetch_all, fetch_groups, fetch_items = range(3)
    attrib_type_int, attrib_type_string = range(2)

    def __init__(self, db):
        self.db            = db
        self.db_metadata   = BoundMetaData(self.db)
        self._table_prefix = ''
        self._table_map    = {}
        self._table_list   = []
        self.__update_table_names()


    def __add_table(self, table):
        self._table_list.append(table)
        self._table_map[table.name] = table


    def __update_table_names(self):
        pfx = self._table_prefix
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
                                 ['action_section.handle'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'resource', self.db_metadata,
            Column('id',             Integer,     primary_key = True),
            Column('section_handle', String(230), index = True),
            Column('handle',         String(230)),
            Column('name',           String(230)),
            Column('n_children',     Integer,     index = True, default = 0),
            Column('is_actor',       Boolean,     index = True),
            Column('is_group',       Boolean,     index = True),
            ForeignKeyConstraint(['section_handle'],
                                 ['resource_section.handle'],
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
                                 ['resource.id'],
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
                                 ['resource.id'],
                                 ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(Table(pfx + 'path_ancestor_map', self.db_metadata,
            Column('resource_path_id',  Integer, index = True),
            Column('ancestor_path_id',  Integer, index = True),
            ForeignKeyConstraint(['resource_path_id'],
                                 ['resource_path.id'],
                                 ondelete = 'CASCADE'),
            ForeignKeyConstraint(['ancestor_path_id'],
                                 ['resource_path.id'],
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


    def debug(self, debug = True):
        self.db.debug = debug


    def set_table_prefix(self, prefix):
        self._table_prefix = prefix
        self.__update_table_names()


    def get_table_prefix(self):
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
                                   tbl_r.c.section_handle == section_handle))
        return self.__get_resource_from_query(select, type)


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
        

    def get_resource_list_from_attribute(self, name, value, type = None):
        assert name  is not None
        assert value is not None
        tbl_a  = self._table_map['resource_attribute']
        tbl_r  = self._table_map['resource']
        table  = outerjoin(tbl_a, tbl_r, tbl_r.c.id == tbl_a.c.resource_id)
        try:
            int(value)
            attr_type = self.attrib_type_int
        except:
            attr_type = self.attrib_type_string
        if attr_type == self.attrib_type_int:
            select = table.select(and_(tbl_a.c.name        == name,
                                       tbl_a.c.type        == attr_type,
                                       tbl_a.c.attr_int    == value),
                                  use_labels = True)
        else:
            select = table.select(and_(tbl_a.c.name        == name,
                                       tbl_a.c.type        == attr_type,
                                       tbl_a.c.attr_string == value),
                                  use_labels = True)
        return self.__get_resource_from_query(select, type, True)


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
                              use_labels = True)

        # Define whether to fetch groups, items, or both.
        if options is self.fetch_groups:
            result = select.execute(is_group = 1)
        elif options is self.fetch_items:
            result = select.execute(is_group = 0)
        elif options is self.fetch_all:
            result = select.execute()
        else:
            assert False

        assert result is not None

        # Collect all children.
        last     = None
        children = [];
        for row in result:
            if row[tbl_r.c.handle] is not last:
                last = row[tbl_r.c.handle]
                resource = self.__get_resource_from_row(row, type)
                resource.set_n_children(row[tbl_r.c.n_children])
                children.append(resource)

            # Append attribute (if any).
            if row[tbl_a.c.name] is None: continue
            if row[tbl_a.c.type] == self.attrib_type_int:
                resource.set_attribute(row[tbl_a.c.name],
                                       int(row[tbl_a.c.attr_int]))
            elif row[tbl_a.c.type] == self.attrib_type_string:
                resource.set_attribute(row[tbl_a.c.name],
                                       row[tbl_a.c.attr_string])

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

        tbl_r  = self._table_map['resource']
        tbl_a  = self._table_map['resource_attribute']
        tbl_p1 = self._table_map['resource_path'].alias('p1')
        tbl_m  = self._table_map['path_ancestor_map']
        tbl_p2 = self._table_map['resource_path'].alias('p2')
        table  = tbl_r.outerjoin(tbl_a,  tbl_r.c.id  == tbl_a.c.resource_id)
        table  = table.outerjoin(tbl_p1, tbl_r.c.id  == tbl_p1.c.resource_id)
        table  = table.outerjoin(tbl_m,  tbl_p1.c.id == tbl_m.c.ancestor_path_id)
        table  = table.outerjoin(tbl_p2, tbl_p2.c.id == tbl_m.c.resource_path_id)
        select = table.select(and_(tbl_p2.c.resource_id == parent_id,
                                   tbl_p2.c.depth       == tbl_p1.c.depth + 1),
                              use_labels = True)
        result = select.execute()
        assert result is not None

        # Collect all parents.
        last    = None
        parents = [];
        for row in result:
            if row[tbl_r.c.handle] is not last:
                last = row[tbl_r.c.handle]
                resource = self.__get_resource_from_row(row, type)
                resource.set_n_children(row[tbl_r.c.n_children])
                parents.append(resource)

            # Append attribute (if any).
            if row[tbl_a.c.name] is None: continue
            if row[tbl_a.c.type] is self.attrib_type_int:
                resource.set_attribute(row[tbl_a.c.name],
                                       int(row[tbl_a.c.attr_int]))
            elif row[tbl_a.c.type] is self.attrib_type_string:
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


    def get_permission_list_from_id(self, actor_id, resource_id):
        assert actor_id    is not None
        assert resource_id is not None

        # **************************************************************
        # * 1. Get all ACLs that match the given resource.
        # **************************************************************
        # All paths that match directly.
        tbl_p1 = self._table_map['resource_path'].alias('p1')

        # All paths that are a parent of the direct match.
        tbl_m1 = self._table_map['path_ancestor_map'].alias('m1')
        tbl = tbl_p1.outerjoin(tbl_m1, tbl_p1.c.id == tbl_m1.c.resource_path_id)

        # Still all paths that are a parent of the direct match, and also the
        # direct match itself.
        tbl_p2 = self._table_map['resource_path'].alias('p2')
        tbl = tbl.outerjoin(tbl_p2, or_(tbl_p2.c.id == tbl_p1.c.id,
                                        tbl_p2.c.id == tbl_m1.c.ancestor_path_id))

        # All ACLs that reference the given resource or any of its parents.
        tbl_ac1 = self._table_map['acl'].alias('ac1')
        tbl = tbl.outerjoin(tbl_ac1, tbl_p2.c.resource_id == tbl_ac1.c.resource_id)

        # Path of the actor that is referenced by the ACL.
        tbl_p3 = self._table_map['resource_path'].alias('p3')
        tbl = tbl.outerjoin(tbl_p3, tbl_p3.c.id == tbl_ac1.c.actor_id)

        # Paths of all children of the actor.
        tbl_m2 = self._table_map['path_ancestor_map'].alias('m2')
        tbl = tbl.outerjoin(tbl_m2, tbl_p3.c.id == tbl_m2.c.ancestor_path_id)

        # Paths of all children of the actor, and also the actor itself.
        tbl_p4 = self._table_map['resource_path'].alias('p4')
        tbl = tbl.outerjoin(tbl_p4, or_(tbl_p4.c.id == tbl_p3.c.id,
                                        tbl_p4.c.id == tbl_m2.c.resource_path_id))

        # Informative only.
        tbl_a1 = self._table_map['action'].alias('a1')
        tbl = tbl.outerjoin(tbl_a1, tbl_a1.c.id == tbl_ac1.c.action_id)
        tbl_s1 = self._table_map['action_section'].alias('s1')
        tbl = tbl.outerjoin(tbl_s1, tbl_a1.c.section_handle == tbl_s1.c.handle)

        # **************************************************************
        # * 2. We want to filter out any ACL that is defined for the
        # * same action but has a shorter actor path.
        # * A side effect of this way of doing it is that ACLs are 
        # * added even if they were not defined for the right actor,
        # * so we need to filter them out in the next step (see 3.).
        # **************************************************************
        # Get all ACLs that control the same action as the ACL above.
        tbl_ac2 = self._table_map['acl'].alias('ac2')
        tbl = tbl.outerjoin(tbl_ac2, tbl_ac1.c.action_id == tbl_ac2.c.action_id)

        # Get a list of all ACLs that perform the same action, but only
        # if their actor path is longer.
        tbl_p5 = self._table_map['resource_path'].alias('p5')
        tbl = tbl.outerjoin(tbl_p5, and_(tbl_ac2.c.actor_id == tbl_p5.c.resource_id,
                                         tbl_p5.c.depth > tbl_p3.c.depth))

        # **************************************************************
        # * 3. Filter out any ACLs that are irrelevant because they do
        # * not have the correct path.
        # **************************************************************
        # Get a list of all actors that are pointed to by the ACL joined
        # above.
        tbl_p6 = self._table_map['resource_path'].alias('p6')
        tbl = tbl.outerjoin(tbl_p6, tbl_p6.c.resource_id == tbl_ac2.c.actor_id)

        # Get their children.
        tbl_m3 = self._table_map['path_ancestor_map'].alias('m3')
        tbl = tbl.outerjoin(tbl_m3, tbl_m3.c.ancestor_path_id == tbl_p6.c.id)

        # Keep only those that are inherited by the wanted actor.
        tbl_p7 = self._table_map['resource_path'].alias('p7')
        tbl = tbl.outerjoin(tbl_p7, or_(tbl_p6.c.id == tbl_p7.c.id,
                                        tbl_m3.c.resource_path_id == tbl_p7.c.id))


        # **************************************************************
        # * 4. We want to filter out any ACL that is defined for the
        # * same action but has a shorter resource path.
        # * A side effect of this way of doing it is that ACLs are
        # * added even if they were not defined for the right resource,
        # * so we need to filter them out in the next step (see 5.).
        # **************************************************************
        # Get all ACLs that control the same action as the ACL above.
        tbl_ac3 = self._table_map['acl'].alias('ac3')
        tbl = tbl.outerjoin(tbl_ac3, tbl_ac1.c.action_id == tbl_ac3.c.action_id)

        # Get a list of all ACLs that perform the same action, but only
        # if their resource path is longer.
        tbl_p8 = self._table_map['resource_path'].alias('p8')
        tbl = tbl.outerjoin(tbl_p8, and_(tbl_ac3.c.resource_id == tbl_p8.c.resource_id,
                                         tbl_p8.c.depth > tbl_p3.c.depth))


        # **************************************************************
        # * 5. Filter out any ACL that is irrelevant because it does
        # * not have the correct path.
        # **************************************************************
        # Get a list of all resources that are pointed to by the ACL
        # joined above.
        tbl_p9 = self._table_map['resource_path'].alias('p9')
        tbl = tbl.outerjoin(tbl_p9, tbl_p9.c.resource_id == tbl_ac3.c.resource_id)

        # Get their children.
        tbl_m4 = self._table_map['path_ancestor_map'].alias('m4')
        tbl = tbl.outerjoin(tbl_m4, tbl_m4.c.ancestor_path_id == tbl_p9.c.id)

        # Keep only those that are inherited by the wanted resource.
        tbl_p10 = self._table_map['resource_path'].alias('p10')
        tbl = tbl.outerjoin(tbl_p10, or_(tbl_p9.c.id == tbl_p10.c.id,
                                         tbl_m4.c.resource_path_id == tbl_p10.c.id))

        #print 'Get: %i,%i' % (actor_id, resource_id)
        p2_max_depth = func.max(tbl_p2.c.depth).label('p2_max_depth')
        p3_max_depth = func.max(tbl_p3.c.depth).label('p3_max_depth')
        sel = select([tbl_ac1.c.actor_id,
                      tbl_ac1.c.resource_id,
                      tbl_ac1.c.permit,
                      tbl_a1,
                      tbl_s1.c.id,
                      tbl_s1.c.handle,
                      tbl_s1.c.name,
                      tbl_p2.c.depth.label('p2_depth'),
                      tbl_p3.c.depth.label('p3_depth'),
                      p2_max_depth,
                      p3_max_depth],
                     and_(tbl_p1.c.resource_id  == resource_id,  # See 1.
                          tbl_p4.c.resource_id  == actor_id,     # See 1.
                          tbl_p5.c.id           == None,         # See 2.
                          tbl_p7.c.resource_id  == actor_id,     # See 3.
                          tbl_p8.c.id           == None,         # See 4.
                          tbl_p10.c.resource_id == resource_id), # See 5.
                     from_obj   = [tbl],
                     use_labels = True,
                     group_by   = [tbl_p2.c.id,
                                   tbl_p3.c.id,
                                   tbl_ac1.c.action_id],
                     having = and_('p2_depth = p2_max_depth',
                                   'p3_depth = p3_max_depth'))
        #print sel
        result = sel.execute()
        assert result is not None

        # Collect all permissions.
        acl_list = [];
        for row in result:
            action  = Action(row[tbl_a1.c.name], row[tbl_a1.c.handle])
            action.set_id(row[tbl_a1.c.id])
            acl = Acl(row[tbl_ac1.c.actor_id],
                      action,
                      row[tbl_ac1.c.resource_id],
                      row[tbl_ac1.c.permit])
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
