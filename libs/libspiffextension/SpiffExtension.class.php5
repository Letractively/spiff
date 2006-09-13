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
// Define allowed dependency patterns.
define('SPIFF_EXTENSION_HANDLE_RE',       '\w+');
define('SPIFF_EXTENSION_VERSION_RE',      '\d+(?:\.\d+)+');
define('SPIFF_EXTENSION_VERSION_OPER_RE', '(?:=|>=)');
define('SPIFF_EXTENSION_DEPENDENCY_RE',   SPIFF_EXTENSION_HANDLE_RE
                                        . '(?:'
                                        .    ' ?'
                                        .    SPIFF_EXTENSION_VERSION_OPER_RE
                                        .    ' ?'
                                        .    SPIFF_EXTENSION_VERSION_RE
                                        . ')?');

class SpiffExtension extends SpiffAclResource {
  protected $version;
  protected $description;
  private   $dependencies;
  
  public function __construct($handle, $name, $version) {
    assert('isset($handle)');
    assert('isset($name)');
    assert('isset($version)');
    $section = new SpiffAclResourceSection('extensions', 'Extensions');
    parent::__construct($handle, $name, $section);
    $this->set_version($version);
    $this->dependencies = array();
  }

  public function set_version($version) {
    assert('isset($version) && $version != ""');
    $this->version = $version;
  }

  public function get_version() {
    return $this->version;
  }

  public function set_description($description) {
    assert('isset($description)');
    $this->description = $description;
  }

  public function get_description() {
    return $this->description;
  }

  public function add_dependency($dependency) {
    assert('isset($dependency) && $dependency != ""');
    $valid_dependency_format = FALSE;
    if (preg_match('/'.SPIFF_EXTENSION_DEPENDENCY_RE.'/', $dependency))
      $valid_dependency_format = TRUE;
    assert('$valid_dependency_format; // $dependency');
    array_push($this->dependencies, $dependency);
  }

  public function get_dependency_list() {
    return $this->dependencies;
  }
}
?>
