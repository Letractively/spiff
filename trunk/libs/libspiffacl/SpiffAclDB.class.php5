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
include_once dirname(__FILE__).'/SpiffAclDBReader.class.php5';

class SpiffAclDB extends SpiffAclDBReader {
  /*******************************************************************
   * Private helper functions.
   *******************************************************************/
  /// Convert an integer to a 8 char wide hexadecimal string.
  /**
   * Given a decimal number, this function returns an 8 character wide
   * hexadecimal string representation.
   */
  private function _int2hex($n)
  {
    assert('is_int($n)');
    return substr("00000000" . dechex($n), -8);
  }


  /// Returns the resource path.
  /**
   * Given a resource id, this function returns the hexadecimal resource
   * path from the database.
   */
  private function _get_resource_path_from_id($id)
  {
    assert('is_int($id)');
    $query = new SqlQuery('
      SELECT HEX(path) path
      FROM   {t_resource_path}
      WHERE  resource_id={id}');
    $query->set_table_names($this->table_names);
    $query->set_int('id', $id);
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    $row  = $rs->FetchRow();
    $len  = strlen($row[0]);
    $path = substr($row[0], 0, $len - 2);
    return $path;
  }


  /*******************************************************************
   * General behavior.
   *******************************************************************/
  /// Installs all database tables that are required by libspiffacl.
  /**
   * Returns TRUE on success, FALSE otherwise.
   */
  public function install()
  {
    $schema = new adoSchema($this->db);
    $schema->SetPrefix($this->db_table_prefix);
    $sql = $schema->ParseSchema(dirname(__FILE__) . '/schema.xml');
    //print_r($sql);
    if ($schema->ExecuteSchema() != 2)
      return FALSE;
    return TRUE;
  }


  /// Clears out the entire database. Use with care.
  /**
   * Wipes out everything, including sections, actions, resources and acls.
   */
  public function clear_database()
  {
    $query = new SqlQuery('DELETE FROM {t_action_section}');
    $query->set_table_names($this->table_names);
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    $query->set_sql('DELETE FROM {t_resource_section}');
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    return TRUE;
  }


  /// Remove everything in the given section from the database. Use with care.
  /**
   */
  public function clear_section(SpiffAclObjectSection &$section)
  {
    assert('is_object($section)');
    $query = new SqlQuery('DELETE FROM {t_action_section}
                           WHERE handle={handle}');
    $query->set_table_names($this->table_names);
    $query->set_string('handle', $section->get_handle());
    //$this->debug();
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    return TRUE;
  }


  /*******************************************************************
   * Object section manipulation.
   *******************************************************************/
  /// Inserts a new section into the database.
  /**
   */
  private function &add_object_section($table,
                                       SpiffAclObjectSection &$section)
  {
    assert('$table === "action_section" || $table === "resource_section"');
    assert('is_object($section)');
    $query = new SqlQuery("
      INSERT INTO {t_$table}
        (handle, name)
      VALUES
        ({handle}, {name})");
    $query->set_table_names($this->table_names);
    $query->set_string('handle', $section->get_handle());
    $query->set_string('name',   $section->get_name());
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    $section->set_id($this->db->Insert_Id());
    return $section;
  }


  /// Saves changes on a section into the database.
  /**
   */
  private function &save_object_section($table,
                                        SpiffAclActionSection &$section)
  {
    assert('$table === "action_section" || $table === "resource_section"');
    assert('is_object($section)');
    assert('$section->get_id() >= 0');
    $query = new SqlQuery("
      UPDATE {t_$table}
      SET    handle={handle}, name={name}
      WHERE  id={id}");
    $query->set_table_names($this->table_names);
    $query->set_int('id',        $section->get_id());
    $query->set_string('handle', $section->get_handle());
    $query->set_string('name',   $section->get_name());
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    return $section;
  }


  /// Deletes a section from the database.
  /**
   */
  private function delete_object_section($table,
                                         SpiffAclObjectSection &$section)
  {
    assert('$table === "action_section" || $table === "resource_section"');
    assert('is_object($section)');
    $query = new SqlQuery("
      DELETE FROM {t_$table}
      WHERE handle={handle}");
    $query->set_table_names($this->table_names);
    $query->set_string('handle', $section->get_handle());
    $rs = $this->db->Execute($query->sql());
    if ($rs)
      $section->set_id(-1);
    return $rs;
  }


  /*******************************************************************
   * Action section manipulation.
   *******************************************************************/
  /// Inserts a new action section into the database.
  /**
   * Action sections group SpiffAclActions into categories.
   */
  public function &add_action_section(SpiffAclActionSection &$section)
  {
    assert('is_object($section)');
    return $this->add_object_section('action_section', $section);
  }


  /// Saves changes on an action section to the database.
  /**
   */
  public function &save_action_section(SpiffAclActionSection &$section)
  {
    assert('is_object($section)');
    return $this->save_object_section('action_section', $section);
  }


  /// Deletes an action section from the database.
  /**
   * All associated actions and ACLs will be deleted. Use with care!
   */
  public function delete_action_section(SpiffAclActionSection &$section)
  {
    assert('is_object($section)');
    return $this->delete_object_section('action_section', $section);
  }


  /*******************************************************************
   * Resource section manipulation.
   *******************************************************************/
  /// Inserts a new resource section into the database.
  /**
   * Resource sections group SpiffAclResources into categories.
   */
  public function &add_resource_section(SpiffAclResourceSection &$section)
  {
    assert('is_object($section)');
    return $this->add_object_section('resource_section', $section);
  }


  /// Saves changes on a resource section to the database.
  /**
   */
  public function &save_resource_section(SpiffAclResourceSection &$section)
  {
    assert('is_object($section)');
    return $this->save_object_section('resource_section', $section);
  }


  /// Deletes a resource section from the database.
  /**
   * All associated resources and ACLs will be deleted. Use with care!
   */
  public function delete_resource_section(SpiffAclResourceSection &$section)
  {
    assert('is_object($section)');
    return $this->delete_object_section('resource_section', $section);
  }


  /*******************************************************************
   * Action manipulation.
   *******************************************************************/
  /// Adds the given SpiffAclAction into the database.
  /**
   * SpiffAclActions define verbs like "view", "edit", "delete", etc.
   */
  public function &add_action(SpiffAclAction &$action,
                              SpiffAclActionSection &$section)
  {
    assert('is_object($action)');
    assert('is_object($section)');
    $query = new SqlQuery('
      INSERT INTO {t_action}
        (section_handle, handle, name)
      VALUES
        ({section_handle}, {handle}, {name})');
    $query->set_table_names($this->table_names);
    $query->set_string('section_handle', $section->get_handle());
    $query->set_string('handle',         $action->get_handle());
    $query->set_string('name',           $action->get_name());
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    $action->set_id($this->db->Insert_Id());
    return $action;
  }


  /// Saves the given SpiffAclAction to the database.
  /**
   */
  public function &save_action(SpiffAclAction &$action,
                               SpiffAclActionSection &$section)
  {
    assert('is_object($action)');
    assert('is_object($section)');
    $query = new SqlQuery('
      UPDATE {t_action}
      SET section_handle={section_handle},
          handle={handle},
          name={name}
      WHERE id={id}');
    $query->set_table_names($this->table_names);
    $query->set_int('id',                $action->get_id());
    $query->set_string('section_handle', $section->get_handle());
    $query->set_string('handle',         $action->get_handle());
    $query->set_string('name',           $action->get_name());
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    return $action;
  }


  /// Deletes the SpiffAclAction with the given id from the database.
  /**
   * All ACLs associated with the SpiffAclAction are removed.
   */
  public function delete_action_from_id($action_id)
  {
    assert('is_int($action_id)');
    $query = new SqlQuery('
      DELETE FROM {t_action}
      WHERE id={action_id}');
    $query->set_table_names($this->table_names);
    $query->set_int('action_id', $action_id);
    return $this->db->Execute($query->sql());
  }


  /// Deletes the given SpiffAclAction from the database.
  /**
   * All ACLs associated with the SpiffAclAction are removed.
   */
  public function delete_action(SpiffAclAction &$action,
                                SpiffAclActionSection &$section)
  {
    assert('is_object($action)');
    assert('is_object($section)');
    $query = new SqlQuery('
      DELETE FROM {t_action}
      WHERE section_handle={section_handle}
      AND   handle={handle}');
    $query->set_table_names($this->table_names);
    $query->set_string('section_handle', $section->get_handle());
    $query->set_string('handle',         $action->get_handle());
    $rs = $this->db->Execute($query->sql());
    if ($rs)
      $action->set_id(-1);
    return $rs;
  }


  /*******************************************************************
   * Resource attributes.
   *******************************************************************/
  private function resource_has_attribute($resource_id, $name)
  {
    $query = new SqlQuery('
     SELECT id
     FROM {t_resource_attribute}
     WHERE resource_id={resource_id} AND name={name}');
    $query->set_table_names($this->table_names);
    $query->set_int('resource_id', $resource_id);
    $query->set_string('name', $name);
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    $row = $rs->FetchRow();
    return $row ? TRUE : FALSE;
  }


  private function resource_add_attribute($resource_id, $name, $value)
  {
    $query = new SqlQuery('
     INSERT INTO {t_resource_attribute}
       (resource_id, name, type, attr_string, attr_int)
     VALUES
       ({resource_id}, {name}, {type}, {attr_string}, {attr_int})');
    $query->set_table_names($this->table_names);
    $query->set_int('resource_id', $resource_id);
    $query->set_string('name', $name);
    if (is_int($value) || is_bool($value)) {
      $query->set_int('type', SPIFF_ACLDB_ATTRIB_TYPE_INT);
      $query->set_int('attr_int', $value);
      $query->set_null('attr_string');
    }
    else {
      $query->set_int('type', SPIFF_ACLDB_ATTRIB_TYPE_STRING);
      $query->set_string('attr_string', $value);
      $query->set_null('attr_int');
    }
    //$this->debug();
    //echo $query->sql() . '<br>';
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    return $this->db->Insert_Id();
  }


  private function resource_update_attribute($resource_id, $name, $value)
  {
    $query = new SqlQuery('
      UPDATE {t_resource_attribute}
      SET type={type},
          attr_string={attr_string},
          attr_int={attr_int}
      WHERE resource_id={resource_id}
      AND   name={name}');
    $query->set_table_names($this->table_names);
    $query->set_int('resource_id', $resource_id);
    $query->set_string('name', $name);
    if (is_numeric($value) || is_bool($value)) {
      $query->set_int('type',     SPIFF_ACLDB_ATTRIB_TYPE_INT);
      $query->set_int('attr_int', $value);
      $query->set_null('attr_string');
    }
    else {
      $query->set_int('type',           SPIFF_ACLDB_ATTRIB_TYPE_STRING);
      $query->set_string('attr_string', $value);
      $query->set_null('attr_int');
    }
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    return TRUE;
  }

  
  /*******************************************************************
   * Resource manipulation.
   *******************************************************************/
  private function resource_add_n_children(SpiffAclResource &$resource, $n)
  {
    assert('$resource->is_group()');
    $query = new SqlQuery('
      UPDATE {t_resource_path}
      SET n_children=n_children + ({n_children})
      WHERE resource_id={resource_id}');
    $query->set_table_names($this->table_names);
    $query->set_int('resource_id', $resource->get_id());
    $query->set_int('n_children',  $n);
    return $this->db->Execute($query->sql());
  }

  
  public function &add_resource($parent_id,
                                SpiffAclResource &$resource,
                                SpiffAclResourceSection &$section)
  {
    assert('is_int($parent_id) || is_null($parent_id)');
    assert('is_object($resource)');
    assert('is_object($section)');

    // Let's take a journey.
    $this->db->StartTrans();

    // Fetch the parent information.
    if (is_null($parent_id))
      $parent_path = '';
    else {
      $parent_path = $this->_get_resource_path_from_id($parent_id);
      $parent      = $this->get_resource_from_id($parent_id);
      $this->resource_add_n_children($parent, 1);
      assert('$parent->is_group()');
    }
    //print "ID: $parent_id/$parent_path<br>";
    assert('strlen($parent_path) / 2 <= 252');

    // Create the resource.
    $query = new SqlQuery('
      INSERT INTO {t_resource}
        (section_handle, handle, name, is_actor, is_group)
      VALUES
        ({section_handle}, {handle}, {name}, {is_actor}, {is_group})');
    $query->set_table_names($this->table_names);
    $query->set_string('section_handle', $section->get_handle());
    $query->set_string('handle',         $resource->get_handle());
    $query->set_string('name',           $resource->get_name());
    $query->set_bool('is_actor',         $resource->is_actor());
    $query->set_bool('is_group',         $resource->is_group());
    //$this->debug();
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    $resource_id = $this->db->Insert_Id();

    // Add a new node into the tree.
    $query = new SqlQuery('
      INSERT INTO {t_resource_path}
        (path, resource_id)
      VALUES
        ({path}, {resource_id})');
    $query->set_table_names($this->table_names);
    $query->set_hex('path',        $parent_path . '0000000000');
    $query->set_int('resource_id', $resource_id);
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    $path_id = (int)$this->db->Insert_Id();

    // Assign the correct path to the new node.
    $query = new SqlQuery('
      UPDATE {t_resource_path}
      SET path={path},
          depth={depth}
      WHERE resource_id={resource_id}');
    //$this->debug();
    $path  = $parent_path . $this->_int2hex($path_id) . '00';
    $depth = strlen($parent_path) / 8;
    //print "PATH: $path, PARENT: $parent_path, DEPTH: $depth<br>\n";
    $query->set_table_names($this->table_names);
    $query->set_hex('path',        $path);
    $query->set_int('depth',       $depth);
    $query->set_int('resource_id', $resource_id);
    //$this->debug();
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');

    // Add a link to every ancestor of the new node into a map
    while ($parent_path != '') {
      //echo "Parent path: $parent_path<br>\n";
      $query = new SqlQuery('
        INSERT INTO {t_path_ancestor_map}
          (resource_path, ancestor_path)
        VALUES
          ({resource_path}, {ancestor_path})');
      $query->set_table_names($this->table_names);
      $query->set_hex('resource_path', $path);
      $query->set_hex('ancestor_path', $parent_path . '00');
      $rs = $this->db->Execute($query->sql());
      assert('is_object($rs)');
      $path_length = strlen($parent_path);
      $parent_path = substr($parent_path, 0, $path_length - 8);
    }

    // Save the attributes.
    foreach ($resource->get_attribute_list() as $attrib_name => $attrib_value) {
      $this->resource_add_attribute($resource_id,
                                    $attrib_name,
                                    $attrib_value);
    }

    // So good being home!
    $this->db->CompleteTrans();
    $resource->set_id($resource_id);
    return $resource;
  }


  public function &save_resource(SpiffAclResource &$resource,
                                 SpiffAclResourceSection &$section)
  {
    assert('is_object($resource)');
    assert('is_object($section)');

    $this->db->StartTrans();
    
    $query = new SqlQuery('
      UPDATE {t_resource}
      SET section_handle={section_handle},
          handle={handle},
          name={name},
          is_actor={is_actor},
          is_group={is_group}
      WHERE id={id}');
    //$this->debug();
    $query->set_table_names($this->table_names);
    $query->set_int('id',                $resource->get_id());
    $query->set_string('section_handle', $section->get_handle());
    $query->set_string('handle',         $resource->get_handle());
    $query->set_string('name',           $resource->get_name());
    $query->set_bool('is_actor',         $resource->is_actor());
    $query->set_bool('is_group',         $resource->is_group());
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');

    // Save the attributes.
    foreach ($resource->get_attribute_list() as $attrib_name => $attrib_value) {
      if ($this->resource_has_attribute($resource->get_id(), $attrib_name))
        $this->resource_update_attribute($resource->get_id(),
                                         $attrib_name,
                                         $attrib_value);
      else
        $this->resource_add_attribute($resource->get_id(),
                                      $attrib_name,
                                      $attrib_value);
    }

    $this->db->CompleteTrans();
    return $resource;
  }

  
  public function delete_resource_from_id($resource_id)
  {
    assert('is_int($resource_id)');
    $query = new SqlQuery('
      DELETE FROM {t_resource}
      WHERE id={resource_id}');
    $query->set_table_names($this->table_names);
    $query->set_string('resource_id', $resource_id);
    return $this->db->Execute($query->sql());
  }


  public function delete_resource(SpiffAclResource &$resource,
                                  SpiffAclResourceSection &$section)
  {
    assert('is_object($resource)');
    assert('is_object($section)');
    $query = new SqlQuery('
      DELETE FROM {t_resource}
      WHERE section_handle={section_handle}
      AND   handle={handle}');
    $query->set_table_names($this->table_names);
    $query->set_string('section_handle', $section->get_handle());
    $query->set_string('handle',         $resource->get_handle());
    $rs = $this->db->Execute($query->sql());
    if ($rs)
      $resource->set_id(-1);
    return $rs;
  }


  /*******************************************************************
   * ACL manipulation.
   *******************************************************************/
  private function add_acl_from_id($actor_id,
                                   $action_id,
                                   $resource_id,
                                   $permit)
  {
    assert('is_int($actor_id)');
    assert('is_int($action_id)');
    assert('is_int($resource_id)');
    assert('is_bool($permit)');
    $query = new SqlQuery('
      INSERT INTO {t_acl}
        (actor_id, action_id, resource_id, permit)
      VALUES
        ({actor_id}, {action_id}, {resource_id}, {permit})');
    $query->set_table_names($this->table_names);
    $query->set_int('actor_id',    $actor_id);
    $query->set_int('action_id',   $action_id);
    $query->set_int('resource_id', $resource_id);
    $query->set_bool('permit',     $permit);
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    return $this->db->Insert_Id();
  }


  private function update_acl_from_id($actor_id,
                                      $action_id,
                                      $resource_id,
                                      $permit)
  {
    assert('is_int($actor_id)');
    assert('is_int($action_id)');
    assert('is_int($resource_id)');
    assert('is_bool($permit)');
    $query = new SqlQuery('
      UPDATE {t_acl}
      SET   permit={permit}
      WHERE actor_id={actor_id}
      AND   action_id={action_id}
      AND   resource_id={resource_id}');
    $query->set_table_names($this->table_names);
    $query->set_int('actor_id',    $actor_id);
    $query->set_int('action_id',   $action_id);
    $query->set_int('resource_id', $resource_id);
    $query->set_bool('permit',     $permit);
    return $this->db->Execute($query->sql());
  }


  private function has_acl_from_id($actor_id,
                                   $action_id,
                                   $resource_id)
  {
    assert('is_int($actor_id)');
    assert('is_int($action_id)');
    assert('is_int($resource_id)');
    $query = new SqlQuery('
      SELECT id
      FROM {t_acl}
      WHERE actor_id={actor_id}
      AND   action_id={action_id}
      AND   resource_id={resource_id}');
    $query->set_table_names($this->table_names);
    $query->set_int('actor_id',    $actor_id);
    $query->set_int('action_id',   $action_id);
    $query->set_int('resource_id', $resource_id);
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    $row = $rs->FetchRow();
    if ($row)
      return TRUE;
    return FALSE;
  }


  public function set_permission_from_id($actor_list,
                                         $action_list,
                                         $resource_list,
                                         $permit)
  {
    if (is_int($actor_list))
      $actor_list = array($actor_list);
    if (is_int($action_list))
      $action_list = array($action_list);
    if (is_int($resource_list))
      $resource_list = array($resource_list);
    assert('is_array($actor_list)');
    assert('is_array($action_list)');
    assert('is_array($resource_list)');
    foreach ($actor_list as $actor_id) {
      foreach ($action_list as $action_id) {
        foreach ($resource_list as $resource_id) {
          if (!$this->has_acl_from_id($actor_id, $action_id, $resource_id))
            $this->add_acl_from_id($actor_id,
                                   $action_id,
                                   $resource_id,
                                   $permit);
          else
            $this->update_acl_from_id($actor_id,
                                      $action_id,
                                      $resource_id,
                                      $permit);
        }
      }
    }
    return TRUE;
  }


  public function set_permission(SpiffAclActor &$actor,
                                 SpiffAclAction &$action,
                                 SpiffAclResource &$resource,
                                 $permit)
  {
    assert('is_object($actor)');
    assert('is_object($action)');
    assert('is_object($resource)');
    assert('is_bool($permit)');
    return $this->set_permission_from_id($actor->get_id(),
                                         $action->get_id(),
                                         $resource->get_id(),
                                         $permit);
  }


  public function grant_from_id($actor_list, $action_list, $resource_list)
  {
    return $this->set_permission_from_id($actor_list,
                                         $action_list,
                                         $resource_list,
                                         TRUE);
  }


  public function grant(SpiffAclActor &$actor,
                        SpiffAclAction &$action,
                        SpiffAclResource &$resource)
  {
    return $this->set_permission($actor,
                                 $action,
                                 $resource,
                                 TRUE);
  }


  public function deny_from_id($actor_list, $action_list, $resource_list)
  {
    return $this->set_permission_from_id($actor_list,
                                         $action_list,
                                         $resource_list,
                                         FALSE);
  }


  public function deny(SpiffAclActor &$actor,
                       SpiffAclAction &$action,
                       SpiffAclResource &$resource)
  {
    return $this->set_permission($actor,
                                 $action,
                                 $resource,
                                 FALSE);
  }
}
?>
