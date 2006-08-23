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

  
  public function get_permission_list_from_id($actor_id, $resource_id)
  {
    assert('is_int($actor_id)');
    assert('is_int($resource_id)');
    $query = new SqlQuery('
      SELECT    a.*, ac.permit, s.id as section_id, s.name as section_name
      FROM      {t_resource_path}     t1
      LEFT JOIN {t_path_ancestor_map} p1 ON t1.path=p1.resource_path
      LEFT JOIN {t_resource_path}     t2 ON t1.id=t2.id
                                         OR t2.path=p1.ancestor_path
      LEFT JOIN {t_acl}               ac ON t2.resource_id=ac.resource_id
      LEFT JOIN {t_resource_path}     t3 ON t3.id=ac.actor_id
      LEFT JOIN {t_path_ancestor_map} p2 ON t3.path=p2.ancestor_path
      LEFT JOIN {t_resource_path}     t4 ON t4.id=t3.id
                                         OR t4.path=p2.resource_path
      LEFT JOIN {t_action}            a  ON a.id=ac.action_id
      LEFT JOIN {t_action_section}    s  ON a.section_handle=s.handle
      WHERE t1.resource_id={resource_id}
      AND   t4.resource_id={actor_id}
      GROUP BY ac.action_id
      ORDER BY t1.path, t2.path, t3.path, t4.path');
    $query->set_table_names($this->table_names);
    $query->set_int('actor_id',    $actor_id);
    $query->set_int('resource_id', $resource_id);
    //$this->debug();
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    $permissions = array();
    while ($row = $rs->FetchRow()) {
      $section = new SpiffAclActionSection($row['section_handle'],
                                      $row['section_name']);
      $action  = new SpiffAclAction($row['handle'], $row['name'], $section);
      $section->set_id($row['section_id']);
      $action->set_id($row['id']);
      unset($perm);
      $perm->action = $action;
      $perm->permit = $row['permit'];
      $permissions[$row['section_handle'] . '_' . $row['handle']] = $perm;
    }
    //print_r($permissions);
    return $permissions;
  }


  public function get_permission_list(SpiffAclActor &$actor,
                                      SpiffAclResource &$resource)
  {
    return $this->get_permission_list_from_id($actor->get_id(),
                                              $resource->get_id());
  }
}
?>
