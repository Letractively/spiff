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
  private $extension_store;
  private $dependencies;
  
  public function __construct($handle, $name, $version = '0') {
    assert('isset($handle)');
    assert('isset($name)');
    assert('isset($version)');
    parent::__construct($name, $handle);
    $this->set_version($version);
    $this->dependencies = array();
  }

  public function set_version($version) {
    assert('isset($version) && $version != ""');
    $this->set_attribute('version', $version);
  }

  public function get_version() {
    return $this->get_attribute('version');
  }

  public function set_author($author) {
    assert('isset($author) && $author != ""');
    $this->set_attribute('author', $author);
  }

  public function get_author() {
    return $this->get_attribute('author');
  }

  public function set_description($description) {
    assert('isset($description)');
    $this->set_attribute('description', $description);
  }

  public function get_description() {
    return $this->get_attribute('description');
  }

  public function set_filename($filename) {
    assert('isset($filename)');
    $this->set_attribute('filename', $filename);
  }

  public function get_filename() {
    return $this->get_attribute('filename');
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

  public function set_extension_store(SpiffExtensionStore &$extension_store) {
    $this->extension_store = $extension_store;
  }

  public function get_extension_store() {
    assert('is_object($this->extension_store)');
    return $this->extension_store;
  }
}
?>
