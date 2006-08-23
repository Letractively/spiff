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
class SpiffAcl {
  private $actor_id;
  private $action;
  private $resource_id;
  private $permit;

  function __construct($actor_id,
                       SpiffAclAction &$action,
                       $resource_id,
                       $permit = FALSE) {
    assert('is_int($actor_id)');
    assert('is_object($action)');
    assert('is_int($resource_id)');
    assert('is_bool($permit)');
    $this->actor_id    = $actor_id;
    $this->action      = $action;
    $this->resource_id = $resource_id;
    $this->permit      = $permit;
  }


  function set_actor_id($id) {
    assert('isset($id)');
    $this->actor_id = (int)$id;
  }


  function get_actor_id() {
    return $this->actor_id;
  }


  function set_action(SpiffAclAction &$action) {
    assert('is_object($assert)');
    $this->action = $action;
  }


  function get_action() {
    return $this->action;
  }


  function set_resource_id($id) {
    assert('isset($id)');
    $this->resource_id = (int)$id;
  }


  function get_resource_id() {
    return $this->resource_id;
  }


  function set_permit($permit) {
    assert('is_bool($permit)');
    $this->permit = $permit;
  }


  function get_permit() {
    return $this->permit;
  }
}
?>

