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
  protected $db;
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
   * Requesting ACLs.
   *******************************************************************/
  /// Returns TRUE if the given actor has the requested permission.
  /**
   * Returns TRUE if the actor with the given id is allowed to perform the
   * action with the given id on the resourcewith the given id.
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
      ORDER BY t1.path, t2.path, t3.path, t4.path
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
  public function get_permission_list_from_id($actor_id, $resource_id)
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
  public function get_permission_list(SpiffAclActor &$actor,
                                      SpiffAclResource &$resource)
  {
    return $this->get_permission_list_from_id($actor->get_id(),
                                              $resource->get_id());
  }
}
?>
