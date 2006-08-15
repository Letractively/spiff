<?php
  /*
  Copyright (C) 2006 Samuel Abels, <spam debain org>

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

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
include_once dirname(__FILE__).'/sql_query.class.php';
include_once dirname(__FILE__).'/../functions/table_names.inc.php';
include_once dirname(__FILE__).'/../functions/config.inc.php';

class GaclActionSection {
  var $name;

  function GaclActionSection($name) {
    $this->name = $name;
  }


  function set_name($name) {
    $this->name = $name;
  }


  function get_name() {
    return $this->name;
  }
}


class GaclAction {
  var $name;
  var $section;
  var $aco;

  function GaclAction($name, $section) {
    $this->name    = $name;
    $this->section = $section;
  }


  function set_name($name) {
    $this->name = $name;
  }


  function get_name() {
    return $this->name;
  }


  function set_section($section) {
    $this->section = $section;
  }


  function get_section() {
    return $this->section;
  }


  function set_id($aco) {
    $this->aco = $aco;
  }


  function get_id() {
    return $this->aco;
  }
}


class GaclResourceSection {
  var $name;

  function GaclResourceSection($name) {
    assert('isset($name)');
    $this->name = $name;
  }


  function set_name($name) {
    assert('isset($name)');
    $this->name = $name;
  }


  function get_name() {
    return $this->name;
  }
}


class GaclResourceGroup {
  var $name;
  var $axo;
  var $n_children;
  var $attributes = array();

  function GaclResourceGroup($name) {
    assert('isset($name)');
    $this->name       = $name;
    $this->axo        = 0;
    $this->n_children = -1;
  }


  function set_name($name) {
    assert('isset($name)');
    $this->name = $name;
  }


  function get_name() {
    return $this->name;
  }


  function set_id($axo) {
    assert('isset($axo)');
    $this->axo = $axo;
  }


  function get_id() {
    return $this->axo;
  }


  function set_n_children($n) {
    assert('isset($n)');
    $this->n_children = $n;
  }


  /// Returns the number of Actors in this group.
  /**
   * \return The number of actors, or -1 if undetermineable.
   */
  function get_n_children() {
    return $this->n_children;
  }


  function set_attribute($name, $value) {
    assert('isset($name)');
    $this->attributes[$name] = $value;
  }


  function get_attribute($name) {
    assert('isset($name)');
    return $this->attributes[$name];
  }


  function &get_attribute_list() {
    return $this->attributes;
  }
}


class GaclResource {
  var $name;
  var $section;
  var $axo;
  var $attributes = array();

  function GaclResource($name, $section) {
    assert('isset($name)');
    assert('is_object($section)');
    $this->name    = $name;
    $this->section = $section;
    $this->axo     = 0;
  }


  function set_name($name) {
    assert('isset($name)');
    $this->name = $name;
  }


  function get_name() {
    return $this->name;
  }


  function set_section($section) {
    assert('is_object($section)');
    $this->section = $section;
  }


  function &get_section() {
    return $this->section;
  }


  function set_id($axo) {
    assert('isset($axo)');
    $this->axo = $axo;
  }


  function get_id() {
    return $this->axo;
  }


  function set_attribute($name, $value) {
    assert('isset($name)');
    $this->attributes[$name] = $value;
  }


  function get_attribute($name) {
    assert('isset($name)');
    return $this->attributes[$name];
  }


  function &get_attribute_list() {
    return $this->attributes;
  }
}


class GaclActorSection {
  var $name;
  var $resource_section;

  function GaclActorSection($name) {
    assert('isset($name)');
    $this->name             = $name;
    $this->resource_section = new GaclResourceSection($name);
  }


  function set_name($name) {
    assert('isset($name)');
    $this->name = $name;
    $this->resource_section->set_name($name);
  }


  function get_name() {
    return $this->name;
  }


  function set_resource_section($resource_section) {
    assert('is_object($resource_section)');
    assert('$resource_section->get_name() === $this->name');
    $this->resource_section = $resource_section;
  }


  function &get_resource_section() {
    return $this->resource_section;
  }
}


class GaclActorGroup {
  var $name;
  var $resource_group;
  var $aro;
  var $n_children;
  var $attributes = array();

  function GaclActorGroup($name) {
    assert(isset($name));
    $this->name           = $name;
    $this->resource_group = new GaclResourceGroup($name);
    $this->aro            = 0;
    $this->n_children     = -1;
  }


  function set_name($name) {
    assert('isset($name)');
    $this->name = $name;
    $this->resource_group->set_name($name);
  }


  function get_name() {
    return $this->resource_group->get_name();
  }


  function set_resource_group($resource_group) {
    assert(is_object($resource_group));
    assert($resource_group->get_name() === $this->name);
    $this->resource_group = $resource_group;
  }


  function &get_resource_group() {
    return $this->resource_group;
  }


  function set_id($aro) {
    assert('isset($aro)');
    $this->aro = $aro;
  }


  function get_id() {
    return $this->aro;
  }


  function set_n_children($n) {
    assert('isset($n)');
    $this->n_children = $n;
  }


  /// Returns the number of Actors in this group.
  /**
   * \return The number of actors, or -1 if undetermineable.
   */
  function get_n_children() {
    return $this->n_children;
  }


  function set_attribute($name, $value) {
    assert('isset($name)');
    $this->attributes[$name] = $value;
  }


  function get_attribute($name) {
    assert('isset($name)');
    return $this->attributes[$name];
  }


  function &get_attribute_list() {
    return $this->attributes;
  }
}

class GaclActor {
  var $name;
  var $section;
  var $resource;
  var $aro;
  var $attributes = array();

  function GaclActor($name, $section) {
    assert('isset($name)');
    assert('is_object($section)');
    $this->name       = $name;
    $resource_section = new GaclResourceSection($section->get_name());
    $this->section    = $section;
    $this->resource   = new GaclResource($name, $resource_section);
    $this->aro        = 0;
  }


  function set_name($name) {
    assert('isset($name)');
    $this->name = $name;
    $this->resource->set_name($name);
  }


  function get_name() {
    return $this->name;
  }


  function set_section($section) {
    assert('is_object($section)');
    $resource_section = new GaclResourceSection($section->get_name());
    $this->section    = $section;
    $this->resource->set_section($resource_section);
  }


  function &get_section() {
    return $this->section;
  }


  function set_resource($resource) {
    assert('is_object($resource)');
    assert($resource->get_name() === $this->name);
    $this->resource = $resource;
  }


  function &get_resource() {
    return $this->resource;
  }


  function set_id($aro) {
    assert('isset($aro)');
    $this->aro = $aro;
  }


  function get_id() {
    return $this->aro;
  }


  function set_attribute($name, $value) {
    assert('isset($name)');
    $this->attributes[$name] = $value;
  }


  function get_attribute($name) {
    assert('isset($name)');
    return $this->attributes[$name];
  }


  function &get_attribute_list() {
    return $this->attributes;
  }
}


class GaclDB {
  var $gacl;
  var $db;
  var $_db_type;
  var $_db_name;
  var $_db_table_prefix;

  function GaclDB($gacl) {
    $this->gacl             = &$gacl;
    $this->db               = &$gacl->db;
    $this->_db_type         = &$gacl->_db_type;
    $this->_db_name         = &$gacl->_db_name;
    $this->_db_table_prefix = &$gacl->_db_table_prefix;
  }


  function _to_sys_name($name) {
    return preg_replace("/[^a-z0-9]/", "", strtolower($name));
  }


  function get_resource_group_id_from_name($name) {
    $sys_name = $this->_to_sys_name($name);
    return $this->gacl->get_group_id($sys_name, $name, 'AXO');
  }


  function get_resource_id_from_name($name, $section) {
    $sys_name      = $this->_to_sys_name($name);
    $sect_sys_name = $this->_to_sys_name($section->get_name());
    return $this->gacl->get_object_id($sect_sys_name, $sys_name, 'AXO');
  }


  function get_actor_group_id_from_name($name) {
    $sys_name = $this->_to_sys_name($name);
    return $this->gacl->get_group_id($sys_name, $name, 'ARO');
  }


  function get_actor_id_from_name($name, $section) {
    $sys_name      = $this->_to_sys_name($name);
    $sect_sys_name = $this->_to_sys_name($section->get_name());
    return $this->gacl->get_object_id($sect_sys_name, $sys_name, 'ARO');
  }


  /// Clear out the database.
  /**
   * This erases all defined sections, including all actions,
   * resources and actors. It erases *everything*. Use with care!
   */
  function clear_database() {
    return $this->gacl->clear_database();
  }


  /// Create a new action section.
  /**
   * It is possible to use different permission types (actions). For
   * example, "view", "edit", and "delete". These actions can be
   * grouped into the sections created by this function.
   * \return The GaclActionSection instance, or FALSE on failure.
   */
  function add_action_section($name) {
    $section = new GaclActionSection($name);
    $res     =  $this->gacl->add_object_section($name,
                                                $this->_to_sys_name($name),
                                                10,
                                                FALSE,
                                                'ACO');
    return $res ? $section : FALSE;
  }


  /// Create a new action.
  /**
   * Use this function to create different permission types (actions); for
   * example, "view", "edit", and "delete".
   * \return A new GaclAction instance, or FALSE on failure.
   */
  function add_action($name, $section) {
    $action           = new GaclAction($name, $section);
    $section_sys_name = $this->_to_sys_name($section->get_name());
    $action->set_id($this->gacl->add_object($section_sys_name,
                                             $name,
                                             $this->_to_sys_name($name),
                                             10,
                                             FALSE,
                                             'ACO'));
    return $action->get_id() ? $action : FALSE;
  }


  /// Create a new resource section.
  /**
   * Resources are the objects that actors want to access. Every
   * resource has to be assigned into a section.
   * \return The GaclResourceSection instance, or FALSE on failure.
   */
  function add_resource_section($name) {
    $section = new GaclResourceSection($name);
    $res     = $this->gacl->add_object_section($name,
                                               $this->_to_sys_name($name),
                                               10,
                                               FALSE,
                                               'AXO');
    return $res ? $section : FALSE;
  }


  /// Create a new resource group.
  /**
   * Resource groups are used to define common criteria of subgroubs and
   * resources.
   * \return The new GaclResourceGroup instance, or FALSE on failure.
   */
  function add_resource_group($parent_group, $name) {
    $group      = new GaclResourceGroup($name);
    $sys_name   = $this->_to_sys_name($name);
    $parent_axo = $parent_group ? $parent_group->get_id() : 0;
    //$this->gacl->_debug = 1; $this->gacl->db->debug = 1;
    $group->set_id($this->gacl->add_group($sys_name,
                                           $name,
                                           $parent_axo,
                                           'AXO'));
    if (!$group->get_id())
      die("add_resource_group(): Ugh");

    // Save attributes.
    $query = new SqlQuery();
    $query->set_int('id', $group->get_id());
    $attrib_fields_sql = 'axo_group_id';
    $attrib_values_sql = '{id}';
    foreach ($group->get_attribute_list() as $key => $val) {
      //echo "Resource group attrib pair: $key: $val<br>";
      $attrib_fields_sql .= ",$key";
      $attrib_values_sql .= ",\{$key}";
      $query->set_var($key, $val);
    }
    $query->set_sql("INSERT INTO {t_axo_groups_attribs}
                    ($attrib_fields_sql)
                    VALUES ($attrib_values_sql)");
    $rs = &$this->db->Execute($query->get_sql());
    if (!$rs)
      die("add_resource_group(): Ugh2");
    return $group;
  }


  /// Delete an existing resource group.
  /**
   * This function removes a resource group from the database.
   * \return TRUE on success, or FALSE on failure.
   */
  function delete_resource_group($resource_group) {
    $res = $this->gacl->del_group($resource_group->get_id(), FALSE, 'AXO');
    return $res;
  }


  function save_resource_group($group) {
    $sys_name = $this->_to_sys_name($group->get_name());
    $res = $gacl->edit_group($group->get_id(),
                             $sys_name,
                             $group->get_name(),
                             NULL,
                             'AXO');
    if (!$res)
      die("save_resource_group(): Ugh");

    // Save attributes.
    $query = new SqlQuery();
    foreach ($group->get_attribute_list() as $key => $val) {
      //echo "Resource group attrib pair: $key: $val<br>";
      if (!isset($attrib_sql))
        $attrib_sql = "SET $key=\{$key}";
      else
        $attrib_sql .= ", $key=\{$key}";
      $query->set_var($key, $val);
    }
    $query->set_sql(
      "UPDATE {t_axo_groups_attribs} at
       $attrib_sql
       WHERE at.axo_group_id={id}");
    $query->set_int('id', $resource->get_id());
    //$this->gacl->_debug = 1; $this->gacl->db->debug = 1;
    $rs = &$this->db->Execute($query->get_sql());
    return $rs;
  }


  function get_resource_group($id) {
    $group_table  = $this->_db_table_prefix . 'axo_groups';
    $attrib_table = $this->_db_table_prefix . 'axo_groups_attribs';
    $query = '
      SELECT a.name, at.*
      FROM      '. $group_table  .' a
      LEFT JOIN '. $attrib_table .' at ON a.id=at.axo_group_id
      WHERE     a.id='. $id * 1 .'
      ORDER BY  a.name
      LIMIT     1';
    $rs             = &$this->db->Execute($query);
    $row            = $rs->FetchObject();
    $resource_group = new GaclResourceGroup($row->NAME);
    $resource_group->set_id($id);
    unset($row['NAME']);
    unset($row['AXO_GROUP_ID']);
    foreach ($row as $key => $var)
      $resource_group->set_attribute(strtolower($key), $var);
    
    return $resource_group;
  }


  /// Create a new resource.
  /**
   * Resources are the objects that are accessed by actors.
   * \return The new GaclResource instance, or FALSE on failure.
   */
  function add_resource($name, $section) {
    $resource = new GaclResource($name, $section);
    $resource->set_id($this->gacl->add_object($this->_to_sys_name($section->get_name()),
                                               $name,
                                               $this->_to_sys_name($name),
                                               10,
                                               FALSE,
                                               'AXO'));
    if (!$resource->get_id())
      die("add_resource(): Ugh");

    // Save attributes.
    $query = new SqlQuery();
    $query->set_int('id', $resource->get_id());
    $attrib_fields_sql = 'axo_id';
    $attrib_values_sql = '{id}';
    foreach ($resource->get_attribute_list() as $key => $val) {
      //echo "Resource attrib pair: $key: $val<br>";
      $attrib_fields_sql .= ",$key";
      $attrib_values_sql .= ",\{$key}";
      $query->set_var($key, $val);
    }
    $query->set_sql("INSERT INTO {t_axo_attribs}
                    ($attrib_fields_sql)
                    VALUES ($attrib_values_sql)");
    $rs = &$this->db->Execute($query->get_sql());
    return $resource;
  }


  /// Delete an existing resource.
  /**
   * Resources are the objects that are accessed by actors.
   * This function removes a resource from the database.
   * \return TRUE on success, or FALSE on failure.
   */
  function delete_resource($resource) {
    $res = $this->gacl->del_object($resource->get_id(), 'AXO', TRUE);
    return $res;
  }


  function save_resource($resource) {
    $sect      = $resource->get_section();
    $sect_name = $this->_to_sys_name($sect->get_name());
    $sys_name  = $this->_to_sys_name($resource->get_name());
    //$this->gacl->_debug = 1; $this->gacl->db->debug = 1;
    $res = $this->gacl->edit_object($resource->get_id(),
                                    $sect_name,
                                    $resource->get_name(),
                                    $sys_name,
                                    10,
                                    FALSE,
                                    'AXO');
    if (!$res)
      die("save_resource(): Ugh");

    // Save attributes.
    $query = new SqlQuery();
    foreach ($resource->get_attribute_list() as $key => $val) {
      //echo "Resource attrib pair: $key: $val<br>";
      if (!isset($attrib_sql))
        $attrib_sql = "SET $key=\{$key}";
      else
        $attrib_sql .= ", $key=\{$key}";
      $query->set_var($key, $val);
    }
    if (!isset($attrib_sql))
      return TRUE;
    $query->set_sql(
      "UPDATE {t_axo_attribs} at
       $attrib_sql
       WHERE at.axo_id={id}");
    $query->set_int('id', $resource->get_id());
    //$this->gacl->_debug = 1; $this->gacl->db->debug = 1;
    $rs = &$this->db->Execute($query->get_sql());
    return $rs;
  }


  function get_resource($id) {
    $group_table   = $this->_db_table_prefix . 'axo';
    $section_table = $this->_db_table_prefix . 'axo_sections';
    $attrib_table  = $this->_db_table_prefix . 'axo_attribs';
    $query = '
      SELECT a.name, s.name as section_name, at.*
      FROM      '. $group_table   .' a
      LEFT JOIN '. $section_table .' s  ON s.value=a.section_value
      LEFT JOIN '. $attrib_table  .' at ON a.id=at.axo_id
      WHERE     a.id='. $id * 1 .'
      ORDER BY  a.name
      LIMIT     1';
    $rs       = &$this->db->Execute($query);
    $row      = $rs->FetchObject();
    $section  = new GaclResourceSection($row->SECTION_NAME);
    $resource = new GaclResource($row->NAME, $section);
    $resource->set_id($id);
    unset($row['NAME']);
    unset($row['SECTION_NAME']);
    unset($row['AXO_ID']);
    foreach ($row as $key => $var)
      $resource->set_attribute(strtolower($key), $var);
    
    return $resource;
  }


  function assign_resource_to_group($resource, $group) {
    $sect      = $resource->get_section();
    $sect_name = $this->_to_sys_name($sect->get_name());
    $sys_name  = $this->_to_sys_name($resource->get_name());
    $axo       = $group->get_id();
    return $this->gacl->add_group_object($axo, $sect_name, $sys_name, 'AXO');
  }


  /// Create a new actor section.
  /**
   * Actors are the objects that request access to a resource.
   * Every actor has to be assigned into a section.
   * Note that every actor has also a resource, so this function
   * automatically generates an actor section AND a resource
   * section with the same name.
   * \return The new GaclActorSection instance, or FALSE on failure.
   */
  function add_actor_section($name) {
    //FIXME: This should be one transaction.
    $section = new GaclActorSection($name);
    $section->set_resource_section($this->add_resource_section($name));
    $res     = $this->gacl->add_object_section($name,
                                               $this->_to_sys_name($name),
                                               10,
                                               FALSE,
                                               'ARO');
    return $res ? $section : FALSE;
  }


  /// Create a new actor group.
  /**
   * Actors groups are used to define common criteria of subgroubs and
   * actors.
   * Note that every actor has also a resource, so this function
   * automatically generates an actor group AND a resource group
   * with the same name.
   * \return The new GaclActorGroup instance, or FALSE on failure.
   */
  function add_actor_group($parent_group, $name) {
    //FIXME: This should be one transaction.
    if (!$parent_group) {
      $root    = new GaclResourceGroup('Root');
      $section = new GaclResourceSection($name);
      $axo     = $this->get_resource_group_id_from_name('Root', $section);
      $root->set_id($axo);
    }
    else
      $root = $parent_group->get_resource_group();
    $group          = new GaclActorGroup($name);
    $group->set_resource_group($this->add_resource_group($root, $name));
    $sys_name       = $this->_to_sys_name($name);
    $parent_aro     = $parent_group ? $parent_group->get_id() : 0;
    $group->set_id($this->gacl->add_group($sys_name,
                                           $name,
                                           $parent_aro,
                                           'ARO'));
    if (!$group->get_id())
      die("add_actor_group(): Ugh");

    // Save attributes.
    $query = new SqlQuery();
    $query->set_int('id', $group->get_id());
    $attrib_fields_sql = 'aro_group_id';
    $attrib_values_sql = '{id}';
    foreach ($group->get_attribute_list() as $key => $val) {
      //echo "Resource group attrib pair: $key: $val<br>";
      $attrib_fields_sql .= ",$key";
      $attrib_values_sql .= ",\{$key}";
      $query->set_var($key, $val);
    }
    $query->set_sql("INSERT INTO {t_aro_groups_attribs}
                    ($attrib_fields_sql)
                    VALUES ($attrib_values_sql)");
    $rs = &$this->db->Execute($query->get_sql());
    if (!$rs)
      die("add_actor_group(): Ugh2");
    return $group;
  }


  /// Delete an existing actor group.
  /**
   * This function removes aa actor group from the database.
   * \return TRUE on success, or FALSE on failure.
   */
  function delete_actor_group($actor_group) {
    //$this->gacl->_debug = 1; $this->gacl->db->debug = 1;
    $resource_group = $actor_group->get_resource_group();
    if (!$this->delete_resource_group($resource_group))
      die("delete_actor_group(): Ugh");
    $res = $this->gacl->del_group($actor_group->get_id(), FALSE, 'ARO');
    return $res;
  }


  function save_actor_group($group) {
    $sys_name = $this->_to_sys_name($group->get_name());
    $res = $this->gacl->edit_group($group->get_id(),
                                   $sys_name,
                                   $group->get_name(),
                                   NULL,
                                   'ARO');
    if (!$res)
      die("save_actor_group(): Ugh");

    // Save attributes.
    $query = new SqlQuery();
    foreach ($group->get_attribute_list() as $key => $val) {
      //echo "Actor group attrib pair: $key: $val<br>";
      if (!isset($attrib_sql))
        $attrib_sql = "SET $key=\{$key}";
      else
        $attrib_sql .= ", $key=\{$key}";
      $query->set_var($key, $val);
    }
    $query->set_sql(
      "UPDATE {t_aro_groups_attribs}
       $attrib_sql
       WHERE aro_group_id={id}");
    $query->set_int('id', $group->get_id());
    //$this->gacl->_debug = 1; $this->gacl->db->debug = 1;
    $rs = &$this->db->Execute($query->get_sql());
    return $rs;
  }


  function get_actor_group($aro) {
    $group_table  = $this->_db_table_prefix . 'aro_groups';
    $attrib_table = $this->_db_table_prefix . 'aro_groups_attribs';
    $query = '
      SELECT a.name, at.*
      FROM      '. $group_table     .' a
      LEFT JOIN '. $attrib_table    .' at ON a.id=at.aro_group_id
      WHERE     a.id='. $aro*1 .'
      ORDER BY  a.name
      LIMIT     1';
    $rs       = &$this->db->Execute($query);
    $row      = $rs->FetchObject();
    $aro_name = $row->NAME;
    unset($row['NAME']);
    unset($row['ARO_GROUP_ID']);

    $axo            = $this->get_resource_group_id_from_name($aro_name);
    $actor_group    = new GaclActorGroup($aro_name);
    $actor_group->set_resource_group($this->get_resource_group($axo));
    $actor_group->set_id($aro);
    foreach ($row as $key => $var)
      $actor_group->set_attribute(strtolower($key), $var);
    
    return $actor_group;
  }


  /// Create a new actor.
  /**
   * Actors are the objects that can request access to a resource.
   * Note that every actor has also a resource, so this function
   * automatically generates an actor AND a resource with the same
   * name.
   * \return The new GaclActor instance, or FALSE on failure.
   */
  function add_actor($name, $section) {
    //FIXME: This should be one transaction.
    //$resource_section = new GaclResourceSection($section->get_name());
    //$section->set_resource_section($resource_section);
    //$resource = &$this->add_resource($name, $resource_section);
    //if (!$resource)
    //  die("add_actor(): Ugh");
    $actor            = new GaclActor($name, $section);
    $resource_section = $section->get_resource_section();
    $actor->set_resource($this->add_resource($name, $resource_section));
    $sect_name        = $this->_to_sys_name($section->get_name());
    //$this->gacl->_debug = 1; $this->gacl->db->debug = 1;
    $actor->set_id($this->gacl->add_object($sect_name,
                                            $name,
                                            $this->_to_sys_name($name),
                                            10,
                                            FALSE,
                                            'ARO'));
    if (!$actor->get_id())
      die("add_actor(): Ugh2");

    // Save attributes.
    $query = new SqlQuery();
    $query->set_int('id', $actor->get_id());
    $attrib_fields_sql = 'aro_id';
    $attrib_values_sql = '{id}';
    foreach ($actor->get_attribute_list() as $key => $val) {
      //echo "Actor attrib pair: $key: $val<br>";
      $attrib_fields_sql .= ",$key";
      $attrib_values_sql .= ",\{$key}";
      $query->set_var($key, $val);
    }
    $query->set_sql("INSERT INTO {t_aro_attribs}
                    ($attrib_fields_sql)
                    VALUES ($attrib_values_sql)");
    $rs = &$this->db->Execute($query->get_sql());
    return $actor;
  }


  /// Delete an existing actor.
  /**
   * This function removes the given actor from the database.
   * \return TRUE on success, or FALSE on failure.
   */
  function delete_actor($actor) {
    $resource = $actor->get_resource();
    $res = $this->delete_resource($resource);
    assert('$res == TRUE');
    $res = $this->gacl->del_object($actor->get_id(), 'ARO', TRUE);
    return $res;
  }


  function save_actor($actor) {
    //FIXME: This should be one transaction.
    //$this->gacl->_debug = 1; $this->gacl->db->debug = 1;
    $res = $this->save_resource($actor->get_resource());
    assert('isset($res)');
    $sect      = $actor->get_section();
    $sect_name = $this->_to_sys_name($sect->get_name());
    $sys_name  = $this->_to_sys_name($actor->get_name());
    $res = $this->gacl->edit_object($actor->get_id(),
                                    $sect_name,
                                    $actor->get_name(),
                                    $sys_name,
                                    10,
                                    FALSE,
                                    'ARO');
    if (!$res)
      die("save_actor(): Ugh");

    // Save attributes.
    $query = new SqlQuery();
    foreach ($actor->get_attribute_list() as $key => $val) {
      //echo "Actor attrib pair: $key: $val<br>";
      if (!isset($attrib_sql))
        $attrib_sql = "SET $key=\{$key}";
      else
        $attrib_sql .= ", $key=\{$key}";
      $query->set_var($key, $val);
    }
    $query->set_sql(
      "UPDATE {t_aro_attribs}
       $attrib_sql
       WHERE aro_id=\{id}");
    $query->set_int('id', $actor->get_id());
    $rs = &$this->db->Execute($query->get_sql());
    return $rs;
  }


  function get_actor($aro) {
    $group_table   = $this->_db_table_prefix . 'aro';
    $section_table = $this->_db_table_prefix . 'aro_sections';
    $attrib_table  = $this->_db_table_prefix . 'aro_attribs';
    $query = '
      SELECT a.name, s.name as section_name, at.*
      FROM      '. $group_table   .' a
      LEFT JOIN '. $section_table .' s  ON s.value=a.section_value
      LEFT JOIN '. $attrib_table  .' at ON a.id=at.aro_id
      WHERE     a.id='. $aro * 1 .'
      ORDER BY  a.name
      LIMIT     1';
    //$this->gacl->_debug = 1; $this->gacl->db->debug = 1;
    $rs               = &$this->db->Execute($query);
    $row              = $rs->FetchObject();
    $aro_name         = $row->NAME;
    $aro_section_name = $row->SECTION_NAME;
    $axo_section      = new GaclResourceSection($aro_section_name);
    $aro_section      = new GaclActorSection($aro_section_name, $axo_section);
    $axo              = $this->get_resource_id_from_name($aro_name, $axo_section);
    $actor            = new GaclActor($aro_name, $aro_section);
    $actor->set_resource($this->get_resource($axo));
    $actor->set_id($aro);
    unset($row['NAME']);
    unset($row['SECTION_NAME']);
    unset($row['ARO_ID']);
    foreach ($row as $key => $var)
      $actor->set_attribute(strtolower($key), $var);
    
    return $actor;
  }


  function assign_actor_to_group($actor, $group) {
    //FIXME: This should be one transaction.
    $this->assign_resource_to_group($actor->get_resource(), $group->get_resource_group());
    $sect      = $actor->get_section();
    $sect_name = $this->_to_sys_name($sect->get_name());
    $sys_name  = $this->_to_sys_name($actor->get_name());
    $aro       = $group->get_id();
    return $this->gacl->add_group_object($aro, $sect_name, $sys_name, 'ARO');
  }


  /// Grant access to a resource.
  /**
   * Sets up an ACL that permits the given actors to perform the
   * given actions on the given resources.
   * \param $actions   An array of actions.
   * \param $actors    An array of actors.
   * \param $resources An array of resources.
   * \return A new ACL instance, or FALSE on failure.
   */
  function grant($actions, $actors, $resources) {
    $aco_array = array();
    foreach ($actions as $action) {
      $name      = $action->get_name();
      $sys_name  = $this->_to_sys_name($name);
      $section   = $action->get_section();
      $sect_name = $this->_to_sys_name($section->get_name());
      if (!isset($aco_array[$sect_name]))
        $aco_array[$sect_name] = array($sys_name);
      else
        array_push($aco_array[$sect_name], $sys_name);
    }

    $aro_array = array();
    foreach ($actors as $actor) {
      $aro = $actor->get_id();
      array_push($aro_array, $aro);
    }

    $axo_array = array();
    foreach ($resources as $resource) {
      $axo = $resource->get_id();
      array_push($axo_array, $axo);
    }

    $allow        = TRUE;
    $enabled      = TRUE;
    $return_value = NULL;
    //$this->gacl->_debug = 1; $this->gacl->db->debug = 1;
    $aclid = $this->gacl->add_acl($aco_array,
                                  NULL,
                                  $aro_array,
                                  NULL,
                                  $axo_array,
                                  $allow,
                                  $enabled,
                                  $return_value,
                                  NULL,
                                  'user');
    return $aclid;
  }


  function &get_resource_group_parent($group) {
    assert('is_object($group)');
    //$this->gacl->_debug = 1; $this->gacl->db->debug = 1;
    $gid = $this->gacl->get_group_parent_id($group->get_id(), 'AXO');
    return $this->get_resource_group($gid);
  }


  function &get_resource_group_list($parent_group, $offset = 0, $limit = 100) {
    assert('is_object($parent_group)');
    $query = new SqlQuery('
      SELECT		a.id, a.name, count(m.axo_id)
      FROM		  {t_axo_groups}     a
      LEFT JOIN {t_groups_axo_map} m ON m.group_id=a.id
      WHERE     a.parent_id={group_id}
      GROUP BY  a.id,a.name
      ORDER BY  a.name
      LIMIT     {offset},{limit}');
    $query->set_int('group_id', $parent_group->get_id());
    $query->set_int('offset',   $offset);
    $query->set_int('limit',    $limit);
    //echo $query->get_sql() . "<br>";
    //$this->gacl->_debug = 1; $this->gacl->db->debug = 1;
    $rs = &$this->db->Execute($query->get_sql());
    assert('isset($rs)');

    $group_list = array();
    if(is_object($rs)) {
      while($row = $rs->FetchRow()) {
        $group = new GaclResourceGroup($row[1]);
        $group->set_id($row[0]);
        $group->set_n_children($row[2]);
        array_push($group_list, $group);
      }
    }
    
    return $group_list;
  }


  function &get_actor_group_list($parent_group, $offset = 0, $limit = 100) {
    assert('is_object($parent_group)');
    $query = new SqlQuery('
      SELECT		a.id, a.name, b.id, count(m.aro_id)
      FROM		  {t_aro_groups}     a
      LEFT JOIN {t_axo_groups}     b ON a.value=b.value
      LEFT JOIN {t_groups_aro_map} m ON m.group_id=a.id
      WHERE     a.parent_id={group_id}
      GROUP BY  a.id,a.name
      ORDER BY  a.name
      LIMIT     {offset},{limit}');
    $query->set_int('group_id', $parent_group->get_id());
    $query->set_int('offset',   $offset);
    $query->set_int('limit',    $limit);
    //echo $query->get_sql() . "<br>";
    //$this->gacl->_debug = 1; $this->gacl->db->debug = 1;
    $rs = &$this->db->Execute($query->get_sql());
    assert('isset($rs)');

    $group_list = array();
    if(is_object($rs)) {
      while($row = $rs->FetchRow()) {
        $group = new GaclActorGroup($row[1]);
        $group->set_id($row[0]);
        $group->set_n_children($row[3]);
        $resource_group = &$group->get_resource_group();
        $resource_group->set_id($row[2]);
        array_push($group_list, $group);
      }
    }
    
    return $group_list;
  }


  function &get_resource_list($parent_group, $offset = 0, $limit = 100) {
    assert('is_object($parent_group)');
    $query = new SqlQuery('
      SELECT		a.id, a.name, s.name section_name
      FROM		  {t_axo}            a
      LEFT JOIN	{t_groups_axo_map} b ON b.axo_id=a.id
      LEFT JOIN {t_axo_sections}   s ON s.value=a.section_value
      WHERE     b.group_id={group_id}
      GROUP BY	a.id,a.name
      ORDER BY  a.name
      LIMIT     {offset},{limit}');
    $query->set_int('group_id', $parent_group->get_id());
    $query->set_int('offset',   $offset);
    $query->set_int('limit',    $limit);
    //echo $query->get_sql() . "<br>";
    //$this->gacl->_debug = 1; $this->gacl->db->debug = 1;
    $rs = &$this->gacl->db->Execute($query->get_sql());
    assert('isset($rs)');

    $resource_list = array();
    if(is_object($rs)) {
      while($row = $rs->FetchRow()) {
        $resource = new GaclResource($row[1], new GaclResourceSection($row[2]));
        $resource->set_id($row[0]);
        array_push($resource_list, $resource);
      }
    }
    
    return $resource_list;
  }


  /// Returns a list of all groups of which the given actor is a member.
  function &get_actor_group_member_list($actor, $offset = 0, $limit = 100) {
    assert('is_object($actor)');
    $query = new SqlQuery('
      SELECT		g.id, g.name, x.id
      FROM		  {t_aro_groups}     g
      LEFT JOIN {t_axo_groups}     x ON g.value=x.value
      LEFT JOIN {t_groups_aro_map} m ON m.group_id=g.id
      WHERE     m.aro_id={id}
      GROUP BY  g.id,g.name
      ORDER BY  g.name
      LIMIT     {offset},{limit}');
    $query->set_int('id',     $actor->get_id());
    $query->set_int('offset', $offset);
    $query->set_int('limit',  $limit);
    //echo $query->get_sql() . "<br>";
    //$this->gacl->_debug = 1; $this->gacl->db->debug = 1;
    $rs = &$this->gacl->db->Execute($query->get_sql());
    assert('isset($rs)');

    $group_list = array();
    if(is_object($rs)) {
      while($row = $rs->FetchRow()) {
        $group = new GaclActorGroup($row[1]);
        $group->set_id($row[0]);
        $resource_group = &$group->get_resource_group();
        $resource_group->set_id($row[2]);
        array_push($group_list, $group);
      }
    }
    return $group_list;
  }


  function &get_actor_list($parent_group, $offset = 0, $limit = 100) {
    assert('is_object($parent_group)');
    $query = new SqlQuery('
      SELECT		a.id, a.name, s.name section_name, x.id
      FROM		  {t_aro}            a
      LEFT JOIN	{t_groups_aro_map} b ON b.aro_id=a.id
      LEFT JOIN {t_aro_sections}   s ON s.value=a.section_value
      LEFT JOIN {t_axo}            x ON x.value=a.value
      WHERE     b.group_id={group_id}
      GROUP BY	a.id,a.name
      ORDER BY  a.name
      LIMIT     {offset},{limit}');
    $query->set_int('group_id', $parent_group->get_id());
    $query->set_int('offset',   $offset);
    $query->set_int('limit',    $limit);
    //echo $query->get_sql() . "<br>";
    //$this->gacl->_debug = 1; $this->gacl->db->debug = 1;
    $rs = &$this->gacl->db->Execute($query->get_sql());
    assert('isset($rs)');

    $actor_list = array();
    if(is_object($rs)) {
      while($row = $rs->FetchRow()) {
        $actor = new GaclActor($row[1], new GaclActorSection($row[2]));
        $actor->set_id($row[0]);
        $resource = &$actor->get_resource();
        $resource->set_id($row[3]);
        array_push($actor_list, $actor);
      }
    }
    
    return $actor_list;
  }


  function get_actor_group_permissions($actor_group,
                                       $resource_group,
                                       $offset = 0,
                                       $limit = 100) {
    $query = new SqlQuery('
      SELECT    ac.name, ac.section_value, a.allow, ac.id, ac.value
      FROM      {t_acl}            a
      LEFT JOIN {t_aro_groups_map} argm ON  a.id=argm.acl_id
      LEFT JOIN {t_axo_groups_map} axgm ON  a.id=axgm.acl_id
      LEFT JOIN {t_aco_map}        acm  ON  a.id=acm.acl_id
      LEFT JOIN {t_aco}            ac   ON  ac.value=acm.value
                                        AND ac.section_value=acm.section_value
      WHERE     a.enabled=1
      AND       argm.group_id={actor_group_id}
      AND       axgm.group_id={resource_group_id}
      ORDER BY  a.updated_DATE DESC');
    //$this->gacl->_debug = 1; $this->db->debug = 1;
    $query->set_int('actor_group_id',    $actor_group->get_id());
    $query->set_int('resource_group_id', $resource_group->get_id());
    $rs = &$this->db->Execute($query->get_sql());
    
    $perms = array();
    if (is_object($rs)) {
      while($row = $rs->FetchRow()) {
        $action = new GaclAction($row[0], $row[1]);
        $action->set_id($row[3]);
        $perm->action = $action;
        $perm->allow  = $row[2];
        $perms[$row[4]] = $perm;
      }
    }
    //print_r($perms);echo "<br>";
    return $perms;
  }


  function get_actor_permissions($actor_group,
                                 $resource_group,
                                 $offset = 0,
                                 $limit = 100) {
    //FIXME
  }
}
?>
