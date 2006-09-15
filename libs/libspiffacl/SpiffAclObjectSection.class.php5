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
include_once dirname(__FILE__).'/functions.inc.php5';

/// Base type for any object sections.
class SpiffAclObjectSection {
  private $id;
  private $handle;
  private $name;

  function __construct($name, $handle = NULL) {
    assert('isset($name)');
    if ($handle == NULL)
      $handle = libspiffacl_mkhandle_from_string($name);
    $this->id     = -1;
    $this->handle = $handle;
    $this->name   = $name;
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
}
?>
