<?php
  /*
  Copyright (C) 2006 Samuel Abels, <spam debain org>

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License version 2, as
  published by the Free Software Foundation.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
  */
?>
<?php
include_once dirname(__FILE__).'/../libuseful/SqlQuery.class.php5';
include_once dirname(__FILE__).'/../libuseful/assert.inc.php';
include_once dirname(__FILE__).'/SpiffAclObjectSection.class.php5';
include_once dirname(__FILE__).'/SpiffAclActionSection.class.php5';
include_once dirname(__FILE__).'/SpiffAclResourceSection.class.php5';
include_once dirname(__FILE__).'/SpiffAcl.class.php5';
include_once dirname(__FILE__).'/SpiffAclAction.class.php5';
include_once dirname(__FILE__).'/SpiffAclResource.class.php5';
include_once dirname(__FILE__).'/SpiffAclResourceGroup.class.php5';
include_once dirname(__FILE__).'/SpiffAclActor.class.php5';
include_once dirname(__FILE__).'/SpiffAclActorGroup.class.php5';

define('SPIFF_ACLDB_ATTRIB_TYPE_STRING', 1);
define('SPIFF_ACLDB_ATTRIB_TYPE_INT',    2);

define('SPIFF_ACLDB_FETCH_GROUPS', 1);
define('SPIFF_ACLDB_FETCH_ITEMS',  2);
define('SPIFF_ACLDB_FETCH_ALL',    3);

class SpiffAclDBReader {
  public    $db;
  protected $db_table_prefix;
  protected $table_names;
  
  
  /// Given an AdoDB connection.
  public function __construct($db)
  {
    assert('is_object($db)');
    $this->db              = $db;
    $this->db_table_prefix = '';
    $this->update_table_names();
  }


  /*******************************************************************
   * Private helper functions.
   *******************************************************************/
  private function update_table_names()
  {
    $this->table_names = array (
      't_action_section'     => $this->db_table_prefix . 'action_section',
      't_resource_section'   => $this->db_table_prefix . 'resource_section',
      't_action'             => $this->db_table_prefix . 'action',
      't_resource'           => $this->db_table_prefix . 'resource',
      't_resource_attribute' => $this->db_table_prefix . 'resource_attribute',
      't_resource_path'      => $this->db_table_prefix . 'resource_path',
      't_path_ancestor_map'  => $this->db_table_prefix . 'path_ancestor_map',
      't_acl'                => $this->db_table_prefix . 'acl',
    );
  }


  /*******************************************************************
   * General behavior.
   *******************************************************************/
  /// Turns debugging messages on/off.
  /**
   * Turns debugging on if TRUE is given, or off if FALSE is given.
   */
  public function debug($debug = 1)
  {
    $this->db->debug = $debug;
  }


  /// Prepends a string before any database table name.
  /**
   */
  public function set_table_prefix($prefix)
  {
    $this->db_table_prefix = $prefix;
    $this->update_table_names();
  }


  /*******************************************************************
   * Requesting actions.
   *******************************************************************/
  public function &get_action_from_id($id)
  {
    assert('is_int($id)');
    assert('$id != -1');
    $query = new SqlQuery('
      SELECT a.*
      FROM  {t_action} a
      WHERE a.id={id}');
    $query->set_table_names($this->table_names);
    $query->set_int('id', $id);
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    $row = $rs->FetchRow();
    $action = new SpiffAclAction($row['name'], $row['handle']);
    $action->set_id($row['id']);
    return $action;
  }


  public function &get_action_from_handle($handle,
                                          SpiffAclActionSection &$section)
  {
    assert('isset($handle)');
    assert('$handle !== ""');
    $query = new SqlQuery('
      SELECT a.*
      FROM      {t_action} a
      WHERE a.handle={handle}
      AND   a.section_handle={section_handle}');
    $query->set_table_names($this->table_names);
    $query->set_string('handle',         $handle);
    $query->set_string('section_handle', $section->get_handle());
    //$this->debug();
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    $row = $rs->FetchRow();
    //print_r($row);
    $action = new SpiffAclAction($row['name'], $row['handle']);
    $action->set_id($row['id']);
    return $action;
  }


  /*******************************************************************
   * Requesting resources.
   *******************************************************************/
  public function &get_resource_from_id($id, $type = NULL)
  {
    assert('is_int($id)');
    assert('$id != -1');
    $query = new SqlQuery('
      SELECT r.*,a.name attr_name,a.type,a.attr_string,a.attr_int
      FROM      {t_resource}           r
      LEFT JOIN {t_resource_attribute} a ON r.id=a.resource_id
      WHERE r.id={id}');
    $query->set_table_names($this->table_names);
    $query->set_int('id', $id);
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    if (!$row = $rs->FetchRow()) {
      $null = NULL;
      return $null;
    }
    if ($type == NULL && $row['is_actor'] && $row['is_group'])
      $type = 'SpiffAclActorGroup';
    else if ($type == NULL && $row['is_actor'])
      $type = 'SpiffAclActor';
    else if ($type == NULL && $row['is_group'])
      $type = 'SpiffAclResourceGroup';
    else if ($type == NULL)
      $type = 'SpiffAclResource';
    else if ($row['is_group'])
      $type .= 'Group';
    //echo "Get type: $type<br>\n";
    $resource = new $type($row['name'], $row['handle']);
    $resource->set_id($row['id']);

    // Append all attributes.
    do {
      switch ($row['type']) {
      case SPIFF_ACLDB_ATTRIB_TYPE_INT:
        $value = (int)$row['attr_int'];
        break;

      case SPIFF_ACLDB_ATTRIB_TYPE_STRING:
        $value = $row['attr_string'];
        break;
      }
      if ($row['attr_name'] != NULL)
        $resource->set_attribute($row['attr_name'], $value);
    } while ($row = $rs->FetchRow());
    return $resource;
  }


  public function &get_resource_from_handle($handle,
                                            $section_handle,
                                            $type = NULL)
  {
    assert('isset($handle)');
    assert('isset($section_handle)');
    $query = new SqlQuery('
      SELECT r.*,a.name attr_name,a.type,a.attr_string,a.attr_int
      FROM      {t_resource}           r
      LEFT JOIN {t_resource_attribute} a ON r.id=a.resource_id
      WHERE r.handle={handle}
      AND   r.section_handle={section_handle}');
    $query->set_table_names($this->table_names);
    $query->set_string('handle',         $handle);
    $query->set_string('section_handle', $section_handle);
    //$this->debug();
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    if (!$row = $rs->FetchRow()) {
      $null = NULL;
      return $null;
    }
    if ($type == NULL && $row['is_actor'] && $row['is_group'])
      $type = 'SpiffAclActorGroup';
    else if ($type == NULL && $row['is_actor'])
      $type = 'SpiffAclActor';
    else if ($type == NULL && $row['is_group'])
      $type = 'SpiffAclResourceGroup';
    else if ($type == NULL)
      $type = 'SpiffAclResource';
    else if ($row['is_group'])
      $type .= 'Group';
    //echo "Get type: $type<br>\n";
    $resource = new $type($row['name'], $row['handle']);
    $resource->set_id($row['id']);

    // Append all attributes.
    do {
      switch ($row['type']) {
      case SPIFF_ACLDB_ATTRIB_TYPE_INT:
        $value = (int)$row['attr_int'];
        break;

      case SPIFF_ACLDB_ATTRIB_TYPE_STRING:
        $value = $row['attr_string'];
        break;
      }
      if ($row['attr_name'] != NULL)
        $resource->set_attribute($row['attr_name'], $value);
    } while ($row = $rs->FetchRow());
    return $resource;
  }


  public function &get_resource_children_from_id($resource_id,
                                                 $type = NULL,
                                                 $options = SPIFF_ACLDB_FETCH_ALL)
  {
    assert('is_int($resource_id)');
    switch ($options) {
    case SPIFF_ACLDB_FETCH_GROUPS:
      $sql = ' AND r.is_group=1';
      break;
      
    case SPIFF_ACLDB_FETCH_ITEMS:
      $sql = ' AND r.is_group=0';
      break;
      
    case SPIFF_ACLDB_FETCH_ALL:
      $sql = '';
      break;

    default:
      assert('FALSE; get_resource_children_from_id(): Invalid option.');
      break;
    }

    $query = new SqlQuery('
      SELECT r.*,a.name attr_name,a.type,a.attr_string,a.attr_int,t1.n_children
      FROM      {t_resource}           r
      LEFT JOIN {t_resource_attribute} a  ON r.id=a.resource_id
      LEFT JOIN {t_resource_path}      t1 ON t1.resource_id=r.id
      LEFT JOIN {t_path_ancestor_map}  p  ON t1.path=p.resource_path
      LEFT JOIN {t_resource_path}      t2 ON t2.path=p.ancestor_path
      WHERE t2.resource_id={resource_id}
      AND   t1.depth=t2.depth + 1'
      . $sql);
    $query->set_table_names($this->table_names);
    $query->set_int('resource_id', $resource_id);
    //$this->debug();
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    $last     = '';
    $children = array();
    while ($row = $rs->FetchRow()) {
      if ($row['handle'] != $last) {
        $last = $row['handle'];
        if ($type == NULL && $row['is_actor'] && $row['is_group'])
          $type = 'SpiffAclActorGroup';
        else if ($type == NULL && $row['is_actor'])
          $type = 'SpiffAclActor';
        else if ($type == NULL && $row['is_group'])
          $type = 'SpiffAclResourceGroup';
        else if ($type == NULL)
          $type = 'SpiffAclResource';
        else if ($row['is_group'])
          $type .= 'Group';
        //echo "Get type: $type<br>\n";
        $child = new $type($row['name'], $row['handle']);
        $child->set_id($row['id']);
        $child->set_n_children($row['n_children']);
        array_push($children, $child);
      }

      // Append all attributes.
      switch ($row['type']) {
      case SPIFF_ACLDB_ATTRIB_TYPE_INT:
        $value = (int)$row['attr_int'];
        break;

      case SPIFF_ACLDB_ATTRIB_TYPE_STRING:
        $value = $row['attr_string'];
        break;
      }
      if ($row['attr_name'] != NULL)
        $child->set_attribute($row['attr_name'], $value);
    }
    //print_r($children);
    return $children;
  }


  public function &get_resource_children(SpiffAclResource &$resource,
                                         $options = SPIFF_ACLDB_FETCH_ALL,
                                         $type = NULL)
  {
    assert('is_object($resource)');
    if (!$resource->is_group()) {
      $list = array();
      return $list;
    }
    return $this->get_resource_children_from_id($resource->get_id(), $options);
  }


  /// Returns a list of all parents of the resource with the given id.
  /**
   * Each resource may have multiple parents, so the result of this
   * method is an array.
   */
  public function &get_resource_parents_from_id($id, $type = NULL)
  {
    assert('is_int($id)');
    assert('$id != -1');
    $query = new SqlQuery('
      SELECT r.*
      FROM      {t_resource}          r
      LEFT JOIN {t_resource_path}     t1 ON t1.resource_id=r.id
      LEFT JOIN {t_path_ancestor_map} p  ON t1.path=p.ancestor_path
      LEFT JOIN {t_resource_path}     t2 ON t2.path=p.resource_path
      WHERE t2.resource_id={id}
      AND   t2.depth=t1.depth + 1');
    $query->set_table_names($this->table_names);
    $query->set_int('id', $id);
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    
    // Each resource may have multiple parents.
    $parents = array();
    while ($row = $rs->FetchRow()) {
      if ($row['is_actor'])
        $parent = new SpiffAclActorGroup($row['name'], $row['handle']);
      else
        $parent = new SpiffAclResourceGroup($row['name'], $row['handle']);
      $parent->set_id($row['id']);
      array_push($parents, $parent);
    }
    
    return $parents;
  }


  /// Returns a list of all parents of the given resource.
  /**
   * Each resource may have multiple parents, so the result of this
   * method is an array.
   * This method is a convenience wrapper around
   * get_resource_parents_from_id();
   */
  public function &get_resource_parents(SpiffAclResource &$resource, $type = NULL)
  {
    assert('is_object($resource)');
    return $this->get_resource_parents_from_id($resource->get_id(), $type = NULL);
  }


  /*******************************************************************
   * Requesting ACLs.
   *******************************************************************/
  /// Returns TRUE if the given actor has the requested permission.
  /**
   * Returns TRUE if the actor with the given id is allowed to perform the
   * action with the given id on the resource with the given id.
   * Returns FALSE otherwise.
   * This method is recursive, so even ACLs that are defined for parents
   * of the given resources are considered if they apply.
   */
  public function has_permission_from_id($actor_id,
                                         $action_id,
                                         $resource_id)
  {
    assert('is_int($actor_id)');
    assert('is_int($action_id)');
    assert('is_int($resource_id)');
    $query = new SqlQuery('
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
      LIMIT    1');
    $query->set_table_names($this->table_names);
    $query->set_int('actor_id',    $actor_id);
    $query->set_int('action_id',   $action_id);
    $query->set_int('resource_id', $resource_id);
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    $row = $rs->FetchRow();
    if (!$row)
      return FALSE;
    return $row[0] == 1 ? TRUE : FALSE;
  }


  /// Returns TRUE if the given actor has the requested permission.
  /**
   * Returns TRUE if the given actor is allowed to perform the given action
   * on the given resource. Returns FALSE otherwise.
   * This method is recursive, so even ACLs that are defined for parents
   * of the given resources are considered if they apply.
   */
  public function has_permission(SpiffAclActor &$actor,
                                 SpiffAclAction &$action,
                                 SpiffAclResource &$resource)
  {
    assert('is_object($actor)');
    assert('is_object($action)');
    assert('is_object($resource)');
    return $this->has_permission_from_id($actor->get_id(),
                                         $action->get_id(),
                                         $resource->get_id());
  }

  
  /// Returns a list of all ACLs that apply between the given resources.
  /**
   * This method is recursive, so even ACLs that are defined for parents
   * of the given resources are returned if they apply.
   */
  public function &get_permission_list_from_id($actor_id, $resource_id)
  {
    assert('is_int($actor_id)');
    assert('is_int($resource_id)');
    $query = new SqlQuery('
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
      AND t3.depth = t3_maxdepth');
    $query->set_table_names($this->table_names);
    $query->set_int('actor_id',    $actor_id);
    $query->set_int('resource_id', $resource_id);
    //$this->debug();
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    $acl_list = array();
    while ($row = $rs->FetchRow()) {
      //print_r($row); print("<br>\n");
      $section = new SpiffAclActionSection($row['section_handle'],
                                      $row['section_name']);
      $action  = new SpiffAclAction($row['handle'], $row['name'], $section);
      $section->set_id($row['section_id']);
      $action->set_id($row['id']);
      $acl = new SpiffAcl((int)$row['actor_id'],
                          $action,
                          (int)$row['resource_id'],
                          (bool)$row['permit']);
      $acl_list[$row['section_handle'] . '_' . $row['handle']] = $acl;
    }
    //print_r($acl_list);
    return $acl_list;
  }


  /// Returns a list of all ACLs that apply between the given resources.
  /**
   * This method is recursive, so even ACLs that are defined for parents
   * of the given resources are returned if they apply.
   */
  public function &get_permission_list(SpiffAclActor &$actor,
                                       SpiffAclResource &$resource)
  {
    return $this->get_permission_list_from_id($actor->get_id(),
                                              $resource->get_id());
  }
}
?>
