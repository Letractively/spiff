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
class SpiffAclAction {
  private $id;
  private $handle;
  private $name;
  private $section;

  function __construct($handle, $name, SpiffAclActionSection &$section) {
    assert('isset($handle)');
    assert('isset($name)');
    assert('is_object($section)');
    $this->id      = -1;
    $this->handle  = $handle;
    $this->name    = $name;
    $this->section = $section;
  }


  function set_id($id) {
    assert('isset($id)');
    $this->id = (int)$id;
  }


  function get_id() {
    return $this->id;
  }


  function set_handle($handle) {
    assert('isset($handle)');
    $this->handle = $handle;
  }


  function get_handle() {
    return $this->handle;
  }


  function set_name($name) {
    assert('isset($name)');
    $this->name = $name;
  }


  function get_name() {
    return $this->name;
  }


  function get_section() {
    return $this->section;
  }
}
?>