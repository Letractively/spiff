import ObjectSection
import ActionSection
import ResourceSection
import Acl
import Action
import ActionGroup
import Resource
import ResourceGroup
import Actor
import ActorGroup

import MySQLdb

class DBReader(object):
    __attrib_type["int"]      = 1
    __attrib_type["string"]   = 2
    __fetch_options["groups"] = 1
    __fetch_options["items"]  = 2
    __fetch_options["all"]    = 3

    def __init__(self, db):
        self.__db           = db
        self.__db_cursor    = db.cursor()
        self.__table_prefix = ''
        self.__table_names  = {}
        self.update_table_names()


    def update_table_names(self):
        pfx = self.__table_prefix
        self.__table_names["t_action_section"]     = pfx + "action_section"
        self.__table_names["t_resource_section"]   = pfx + "resource_section"
        self.__table_names["t_action"]             = pfx + "action"
        self.__table_names["t_resource"]           = pfx + "resource"
        self.__table_names["t_resource_attribute"] = pfx + "resource_attribute"
        self.__table_names["t_resource_path"]      = pfx + "resource_path"
        self.__table_names["t_path_ancestor_map"]  = pfx + "path_ancestor_map"
        self.__table_names["t_acl"]                = pfx + "acl"


    def debug(self, debug = True):
        self.db.debug = debug


    def set_table_prefix(self, prefix):
        self.__table_prefix = prefix


    def get_action_from_query(self, query):
        assert query not None
        self.__db_cursor.execute(query.sql)
        row = self.__db_cursor.fetchone()
        if not row: return None
        action = Action(row["name"], row["handle"])
        action.set_id(row["id"])
        return action


    def get_action_from_id(self, id):
        assert id not None
        query = SqlQuery(self.__table_names, """
            SELECT a.*
            FROM  {t_action} a
            WHERE a.id={id}""")
        query.set_int("id", id)
        return self.get_action_from_query(query)


    def get_action_from_handle(self, handle, section_handle):
        assert handle         not None
        assert section_handle not None
        query = SqlQuery(self.__table_names, """
            SELECT a.*
            FROM  {t_action} a
            WHERE a.handle={handle}
            AND   a.section_handle={section_handle}""")
        query.set_string("handle",         handle)
        query.set_string("section_handle", section_handle)
        return self.get_action_from_query(query)


    def get_resource_from_row(self, row, type = None):
        if not row: return None
        if not type and row["is_actor"]:
            type = "Actor"
        elif not type and not row["is_actor"]
            type = "Resource"
        if row["is_group"]:
            type.append("Group")
        #print "Type", type
        resource = type(row["name"], row["handle"])
        resource.set_id(row["id"])
        return resource


    def get_resource_from_query(self, query, type = None):
        assert query not None
        self.__db_cursor.execute(query.sql)
        row = self.__db_cursor.fetchone()
        resource = self.get_resource_from_row(row, type)
        if not resource: return None

        # Append all attributes.
        while 1:
            # Determine attribute type.
            if row["type"] is self.__attrib_type["int"]:
                value = int(row["attr_int"])
            elif row["type"] is self.__attrib_type["string"]:
                value = row["string"]

            # Append attribute.
            if row["attr_name"] not None:
                resource.set_attribute(row["attr_name"], value)
            row = self.__db_cursor.fetchone()
            if not row: break
            
        return resource


    def get_resource_from_id(self, id, type = None):
        assert id >= 0
        query = SqlQuery(self.__table_names, """
            SELECT r.*,a.name attr_name,a.type,a.attr_string,a.attr_int
            FROM      {t_resource}           r
            LEFT JOIN {t_resource_attribute} a ON r.id=a.resource_id
            WHERE r.id={id}""")
        query.set_int("id", id)
        return self.get_resource_from_query(query, type)
        

    def get_resource_from_handle(self, handle, section_handle, type = None):
        assert handle         not None
        assert section_handle not None
        query = SqlQuery(self.__table_names, """
            SELECT r.*,a.name attr_name,a.type,a.attr_string,a.attr_int
            FROM      {t_resource}           r
            LEFT JOIN {t_resource_attribute} a ON r.id=a.resource_id
            WHERE r.handle={handle}
            AND   r.section_handle={section_handle}""")
        query.set_string("handle",         handle)
        query.set_string("section_handle", section_handle)
        return self.get_resource_from_query(query, type)


    def get_resource_from_name(self, name, section_handle, type = None):
        assert name           not None
        assert section_handle not None
        query = SqlQuery(self.__table_names, """
            SELECT r.*,a.name attr_name,a.type,a.attr_string,a.attr_int
            FROM      {t_resource}           r
            LEFT JOIN {t_resource_attribute} a ON r.id=a.resource_id
            WHERE r.name={name}
            AND   r.section_handle={section_handle}""")
        query.set_string("name",           name)
        query.set_string("section_handle", section_handle)
        return self.get_resource_from_query(query, type)


    def get_resource_children_from_id(self,
                                      resource_id,
                                      type = None,
                                      options = self.__fetch_options["all"]):
        assert resource_id not None

        # Define whether to fetch groups, items, or both.
        if options is self.__fetch_options["groups"]:
            sql = " AND r.is_group=1"
        elif options is self.__fetch_options["items"]:
            sql = " AND r.is_group=0"
        elif options is self.__fetch_options["all"]:
            sql = ""
        else:
            assert False

        query = SqlQuery(self.__table_names, """
            SELECT r.*,a.name attr_name,a.type,a.attr_string,a.attr_int,t1.n_children
            FROM      {t_resource}           r
            LEFT JOIN {t_resource_attribute} a  ON r.id=a.resource_id
            LEFT JOIN {t_resource_path}      t1 ON t1.resource_id=r.id
            LEFT JOIN {t_path_ancestor_map}  p  ON t1.path=p.resource_path
            LEFT JOIN {t_resource_path}      t2 ON t2.path=p.ancestor_path
            WHERE t2.resource_id={resource_id}
            AND   t1.depth=t2.depth + 1""" + sql)
        query.set_int("resource_id", resource_id)
        self.__db_cursor.execute(query.sql)

        # Collect all children.
        last     = None
        children = [];
        while 1:
            row = self.__db_cursor.fetchone()
            if not row: break
            if row["handle"] not last:
                last = row["handle"]
                resource = self.get_resource_from_row(row, type)
                resource.set_n_children(row["n_children"])
                children.append(resource)

            # Append attribute (if any).
            if row["attr_name"] is None: continue
            if row["type"] is self.__attrib_type["int"]:
                resource.set_attribute(row["name"], int(row["attr_int"]))
            elif row["type"] is self.__attrib_type["string"]:
                resource.set_attribute(row["name"], row["attr_string"])

        return children


    def get_resource_children(self,
                              resource,
                              type = None,
                              options = self.__fetch_options["all"]):
        assert resource not None
        if not resource.is_group(): return []
        resource_id = resource.get_id()
        return self.get_resource_children_from_id(resource_id, type, options)


    def get_resource_parents_from_id(self, parent_id, type = None):
        assert parent_id >= 0
        query = SqlQuery(self.__table_names, """
            SELECT r.*,a.name attr_name,a.type,a.attr_string,a.attr_int,t1.n_children
            FROM      {t_resource}           r
            LEFT JOIN {t_resource_attribute} a  ON r.id=a.resource_id
            LEFT JOIN {t_resource_path}      t1 ON t1.resource_id=r.id
            LEFT JOIN {t_path_ancestor_map}  p  ON t1.path=p.ancestor_path
            LEFT JOIN {t_resource_path}      t2 ON t2.path=p.resource_path
            WHERE t2.resource_id={resource_id}
            AND   t2.depth=t1.depth + 1""")
        query.set_int("resource_id", parent_id)
        self.__db_cursor.execute(query.sql)

        # Collect all parents.
        last    = None
        parents = [];
        while 1:
            row = self.__db_cursor.fetchone()
            if not row: break
            if row["handle"] not last:
                last = row["handle"]
                resource = self.get_resource_from_row(row, type)
                resource.set_n_children(row["n_children"])
                parents.append(resource)

            # Append attribute (if any).
            if row["attr_name"] is None: continue
            if row["type"] is self.__attrib_type["int"]:
                resource.set_attribute(row["name"], int(row["attr_int"]))
            elif row["type"] is self.__attrib_type["string"]:
                resource.set_attribute(row["name"], row["attr_string"])

        return parents


    def get_resource_parents(self, resource, type = None):
        assert resource not None
        return self.get_resource_parents_from_id(resource.get_id(), type)


    def has_permission_from_id(self, actor_id, action_id, resource_id):
        assert actor_id    not None
        assert action_id   not None
        assert resource_id not None
        query = SqlQuery(self.__table_names, """
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
            LIMIT    1""")
        query.set_int("actor_id",    actor_id)
        query.set_int("action_id",   action_id)
        query.set_int("resource_id", resource_id)
        self.__db_cursor.execute(query.sql)
        row = self.__db_cursor.fetchone()
        if not row: return False
        if row[0] is 1: return True
        return False


    def has_permission(self, actor, action, resource):
        assert actor    not None
        assert action   not None
        assert resource not None
        actor_id    = actor.get_id()
        action_id   = action.get_id()
        resource_id = resource.get_id()
        return self.has_permission_from_id(actor_id, action_id, resource_id)


    def get_permission_list_from_id(self, actor_id, resource_id):
        assert actor_id    not None
        assert resource_id not None
        query = SqlQuery(self.__table_names, """
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
            AND t3.depth = t3_maxdepth""")
        query.set_int("actor_id",    actor_id)
        query.set_int("resource_id", resource_id)
        self.__db_cursor.execute(query.sql)

        # Collect all permissions.
        acl_list = [];
        while 1:
            row = self.__db_cursor.fetchone()
            if not row: break
            section = ActionSection(row["section_name"], row["section_handle"])
            action  = Action(row["name"], row["handle"], section)
            section.set_id(row["section_id"])
            action.set_id(row["id"])
            acl = Acl(row["actor_id"],
                      action,
                      row["resource_id"],
                      row["permit"])
            acl_list.append(acl)
        
        return acl_list


    def get_permission_list(self, actor, resource):
        assert actor    not None
        assert resource not None
        actor_id    = actor.get_id()
        resource_id = resource.get_id()
        return self.get_permission_list_from_id(actor_id, resource_id)
