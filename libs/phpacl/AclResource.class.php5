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
class AclResource {
  private $id;
  private $handle;
  private $name;
  private $section;
  private $n_children;
  private $attributes = array();

  public function __construct($handle, $name, AclObjectSection &$section) {
    assert('isset($handle)');
    assert('isset($name)');
    assert('is_object($section)');
    $this->id         = -1;
    $this->handle     = $handle;
    $this->name       = $name;
    $this->section    = $section;
    $this->n_children = 0;
  }


  public function get_section() {
    return $this->section;
  }


  public function set_id($id) {
    assert('isset($id)');
    $this->id = (int)$id;
  }


  public function get_id() {
    return $this->id;
  }


  public function set_handle($handle) {
    assert('isset($handle)');
    $this->handle = $handle;
  }


  public function get_handle() {
    return $this->handle;
  }


  public function set_name($name) {
    assert('isset($name)');
    $this->name = $name;
  }


  public function get_name() {
    return $this->name;
  }


  public function is_actor() {
    return FALSE;
  }


  public function is_group() {
    return FALSE;
  }


  public function set_n_children($n_children) {
    assert('isset($n_children)');
    $this->n_children = $n_children;
  }


  /// Returns the number of objects in this group.
  public function get_n_children() {
    return $this->n_children;
  }


  public function set_attribute($name, $value) {
    assert('isset($name)');
    $this->attributes[$name] = $value;
  }


  public function get_attribute($name) {
    assert('isset($name)');
    return $this->attributes[$name];
  }


  public function &get_attribute_list() {
    return $this->attributes;
  }
}
?>
