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
class SpiffPlugin {
  private $spiff;
  protected $name;
  protected $sys_name;
  protected $version;
  protected $description;
  private $dependencies;
  
  private function __constructor(Spiff &$spiff) {
    $this->spiff        = $spiff;
    $this->dependencies = array();
  }

  public function set_name($name) {
    assert('isset($name) && $name != ""');
    $this->name = $name;
  }

  public function get_name() {
    return $this->name;
  }

  public function set_sys_name($sys_name) {
    assert('isset($sys_name) && $sys_name != ""');
    $this->sys_name = $sys_name;
  }

  public function get_sys_name() {
    return $this->sys_name;
  }

  public function set_version($version) {
    assert('isset($version) && $version != ""');
    $this->version = $version;
  }

  public function get_version() {
    return $this->version;
  }

  public function set_description($description) {
    assert('isset($description) && $description != ""');
    $this->description = $description;
  }

  public function get_description() {
    return $this->description;
  }

  public function add_dependency($dependency) {
    assert('isset($dependency) && $dependency != ""');
    array_push($this->dependencies, $dependency);
  }

  public function get_dependency_list() {
    return $this->dependencies;
  }

  public function register_callback($name, $function) {
    assert('isset($name) && $name != ""');
    assert('isset($function));
    $this->spiff->get_bus->register($name, $function); //FIXME
  }
}
?>
