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


  function set_aco($aco) {
    $this->aco = $aco;
  }


  function get_aco() {
    return $this->aco;
  }
}


class GaclResourceSection {
  var $name;

  function GaclResourceSection($name) {
    $this->name    = $name;
  }


  function set_name($name) {
    $this->name = $name;
  }


  function get_name() {
    return $this->name;
  }
}


class GaclResourceGroup {
  var $name;
  var $axo;
  var $attributes = array();

  function GaclResourceGroup($name) {
    $this->name = $name;
  }


  function set_name($name) {
    $this->name = $name;
  }


  function get_name() {
    return $this->name;
  }


  function set_axo($axo) {
    $this->axo = $axo;
  }


  function get_axo() {
    return $this->axo;
  }


  function set_attribute($name, $value) {
    $this->attributes[$name] = $value;
  }


  function get_attribute($name) {
    return $this->attributes[$name];
  }
}


class GaclResource {
  var $name;
  var $section;
  var $axo;
  var $attributes = array();

  function GaclResource($name, $section) {
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


  function set_axo($axo) {
    $this->axo = $axo;
  }


  function get_axo() {
    return $this->axo;
  }


  function set_attribute($name, $value) {
    $this->attributes[$name] = $value;
  }


  function get_attribute($name) {
    return $this->attributes[$name];
  }
}


class GaclActorSection {
  var $name;
  var $resource_section;

  function GaclActorSection($name, $resource_section) {
    $this->name             = $name;
    $this->resource_section = $resource_section;
  }


  function set_name($name) {
    $this->name = $name;
  }


  function get_name() {
    return $this->name;
  }
}


class GaclActorGroup {
  var $name;
  var $resource_group;
  var $aro;
  var $attributes = array();

  function GaclActorGroup($name, $resource_group) {
    $this->name           = $name;
    $this->resource_group = $resource_group;
  }


  function set_name($name) {
    $this->name = $name;
  }


  function get_name() {
    return $this->name;
  }


  function set_resource_group($resource_group) {
    $this->resource_group = $resource_group;
  }


  function get_resource_group() {
    return $this->resource_group;
  }


  function set_aro($aro) {
    $this->aro = $aro;
  }


  function get_aro() {
    return $this->aro;
  }


  function set_attribute($name, $value) {
    $this->attributes[$name] = $value;
  }


  function get_attribute($name) {
    return $this->attributes[$name];
  }
}

class GaclActor {
  var $name;
  var $section;
  var $resource;
  var $aro;
  var $attributes = array();

  function GaclActor($name, $section, $resource) {
    $this->name     = $name;
    $this->section  = $section;
    $this->resource = $resource;
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


  function set_resource($resource) {
    $this->resource = $resource;
  }


  function get_resource() {
    return $this->resource;
  }


  function set_aro($aro) {
    $this->aro = $aro;
  }


  function get_aro() {
    return $this->aro;
  }


  function set_attribute($name, $value) {
    $this->attributes[$name] = $value;
  }


  function get_attribute($name) {
    return $this->attributes[$name];
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


  function get_resource_group_id_from_name($name, $section) {
    $sys_name      = $this->_to_sys_name($name);
    $sect_sys_name = $this->_to_sys_name($section->get_name());
    return $this->gacl->get_group_id($name, $sect_sys_name, 'AXO');
  }


  function get_resource_id_from_name($name, $section) {
    $sys_name      = $this->_to_sys_name($name);
    $sect_sys_name = $this->_to_sys_name($section->get_name());
    return $this->gacl->get_object_id($sect_sys_name, $sys_name, 'AXO');
  }


  function get_actor_group_id_from_name($name, $section) {
    $sys_name      = $this->_to_sys_name($name);
    $sect_sys_name = $this->_to_sys_name($section->get_name());
    return $this->gacl->get_group_id($name, $sect_sys_name, 'ARO');
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
    $action->set_aco($this->gacl->add_object($section_sys_name,
                                             $name,
                                             $this->_to_sys_name($name),
                                             10,
                                             FALSE,
                                             'ACO'));
    return $action->get_aco() ? $action : FALSE;
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
    $parent_axo = $parent_group ? $parent_group->get_axo() : 0;
    //$this->gacl->_debug = 1; $this->gacl->db->debug = 1;
    $group->set_axo($this->gacl->add_group($sys_name,
                                           $name,
                                           $parent_axo,
                                           'AXO'));
    return $group->get_axo() ? $group : FALSE;
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
    $resource_group->set_axo($id);
    unset($row['NAME']);
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
    $resource->set_axo($this->gacl->add_object($this->_to_sys_name($section->get_name()),
                                               $name,
                                               $this->_to_sys_name($name),
                                               10,
                                               FALSE,
                                               'AXO'));
    return $resource->get_axo() ? $resource : FALSE;
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
    $resource->set_axo($id);
    unset($row['NAME']);
    unset($row['SECTION_NAME']);
    foreach ($row as $key => $var)
      $resource->set_attribute(strtolower($key), $var);
    
    return $resource;
  }


  function assign_resource_to_group($resource, $group) {
    $sect      = $resource->get_section();
    $sect_name = $this->_to_sys_name($sect->get_name());
    $sys_name  = $this->_to_sys_name($resource->get_name());
    $axo       = $group->get_axo();
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
    $resource_section = $this->add_resource_section($name);
    $section = new GaclActorSection($name, $resource_section);
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
      $root->set_axo($axo);
    }
    else
      $root = $parent_group->get_resource_group();
    $resource_group = $this->add_resource_group($root, $name);
    $group          = new GaclActorGroup($name, $resource_group);
    $sys_name       = $this->_to_sys_name($name);
    $parent_aro     = $parent_group ? $parent_group->get_aro() : 0;
    $group->set_aro($this->gacl->add_group($sys_name,
                                           $name,
                                           $parent_aro,
                                           'ARO'));
    return $group->get_aro() ? $group : FALSE;
  }


  function get_actor_group($aro) {
    $group_table  = $this->_db_table_prefix . 'aro_groups';
    $attrib_table = $this->_db_table_prefix . 'aro_groups_attribs';
    $query = '
      SELECT a.name, a.value, at.*
      FROM      '. $group_table     .' a
      LEFT JOIN '. $attrib_table    .' at ON a.id=at.aro_group_id
      WHERE     a.id='. $aro*1 .'
      ORDER BY  a.name
      LIMIT     1';
    $rs               = &$this->db->Execute($query);
    $row              = $rs->FetchObject();
    $aro_name         = $row->NAME;
    $aro_section_name = $row->VALUE;
    unset($row['NAME']);
    unset($row['VALUE']);

    $section        = new GaclResourceSection($aro_section_name);
    $axo            = $this->get_resource_group_id_from_name($aro_name, $section);
    $resource_group = $this->get_resource_group($axo);

    $actor_group = new GaclActorGroup($aro_name, $resource_group);
    $actor_group->set_aro($aro);
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
    $resource  = $this->add_resource($name, $section);
    $actor     = new GaclActor($name, $section, $resource);
    $sect_name = $this->_to_sys_name($section->get_name());
    $actor->set_aro($this->gacl->add_object($sect_name,
                                            $name,
                                            $this->_to_sys_name($name),
                                            10,
                                            FALSE,
                                            'ARO'));
    return $actor->get_aro() ? $actor : FALSE;
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
    $resource         = $this->get_resource($axo);
    $actor            = new GaclActor($aro_name, $aro_section, $resource);
    $actor->set_aro($aro);
    unset($row['NAME']);
    unset($row['SECTION_NAME']);
    foreach ($row as $key => $var)
      $actor->set_attribute(strtolower($key), $var);
    
    return $resource;
  }


  function assign_actor_to_group($actor, $group) {
    //FIXME: This should be one transaction.
    $this->assign_resource_to_group($actor->get_resource(), $group->get_resource_group());
    $sect      = $actor->get_section();
    $sect_name = $this->_to_sys_name($sect->get_name());
    $sys_name  = $this->_to_sys_name($actor->get_name());
    $aro       = $group->get_aro();
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
      $aro = $actor->get_aro();
      array_push($aro_array, $aro);
    }

    $axo_array = array();
    foreach ($resources as $resource) {
      $axo = $resource->get_axo();
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
}

new GaclDB(NULL);
?>
