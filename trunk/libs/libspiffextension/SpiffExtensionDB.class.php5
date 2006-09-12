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
include_once dirname(__FILE__).'/../libuseful/SqlQuery.class.php5';
include_once dirname(__FILE__).'/../libuseful/assert.inc.php';
include_once dirname(__FILE__).'/../libspiffacl/SpiffAclDB.class.php5';
include_once dirname(__FILE__).'/SpiffExtension.class.php5';

class SpiffExtensionDB {
  private $acldb;
  private $acl_section;
  private $db;
  private $db_table_prefix;
  
  function __constructor(SpiffAclDB &$acldb)
  {
    $this->acldb           = $acldb;
    $this->acl_section     = new SpiffAclResourceSection('extensions');
    $this->db              = $acldb->db;
    $this->db_table_prefix = '';
    $this->update_table_names();
  }


  /*******************************************************************
   * Private helper functions.
   *******************************************************************/
  private function update_table_names()
  {
    $this->table_names = array (
      't_extension'                => $this->db_table_prefix . 'extension',
      't_extension_dependency'     => $this->db_table_prefix . 'extension_dependency',
      't_extension_dependency_map' => $this->db_table_prefix . 'extension_dependency_map'
    );
  }


  /// Returns TRUE if $version_a is greater than $version_b.
  /**
   * \return Boolean.
   */
  private function version_is_greater($version_a, $version_b)
  {
    // Split the version string into the components separated by dots.
    $a_numbers = explode('.', $version);
    $b_numbers = explode('.', $installed_version);

    // Walk through all the numbers of the version string.
    for ($i = 0;
         isset($a_numbers[$i]) || isset($b_numbers[$i]);
         $i++) {
      // Postfix shorter versions with zeros to make comparison possible.
      if (!isset($a_numbers[$i]))
        $a_numbers[$i] = 0;
      if (!isset($b_numbers[$i]))
        $b_numbers[$i]  = 0;

      // Convert to int, so that strings like "2.1.build123" will also work.
      settype($a_numbers[$i], 'integer');
      settype($b_numbers[$i], 'integer');

      // The current installed version number has to be greater or equal.
      if ($a_numbers[$i] < $b_numbers[$i])
        return FALSE;
    }

    return TRUE;
  }


  /*******************************************************************
   * General behavior.
   *******************************************************************/
  /// Turns debugging messages on/off.
  /**
   * Turns debugging on if TRUE is given, or off if FALSE is given.
   */
  public function debug($debug = 1)
  {
    $this->db->debug = $debug;
  }


  /// Prepends a string before any database table name.
  /**
   */
  public function set_table_prefix($prefix)
  {
    $this->db_table_prefix = $prefix;
    $this->update_table_names();
  }


  /*******************************************************************
   * Dependency table functions.
   *******************************************************************/
  /// Check whether the given extension depends on the given dependency.
  /**
   * \return Boolean.
   */
  private function has_dependency_link($extension_id, $dependency_id)
  {
    $query = new SqlQuery('
      SELECT extension_id FROM {t_extension_dependency_map}
      WHERE extension_id={extension_id}
      AND   dependency_id={dependency_id}');
    $query->set_table_names($this->table_names);
    $query->set_int('extension_id',  $extension_id);
    $query->set_int('dependency_id', $dependency_id);
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    $row = $rs->FetchRow();
    return $row ? TRUE : FALSE;
  }


  /// Links the given extension with the given dependency.
  /**
   * Links the extension with the given id with the dependency with
   * the given id.
   * \return TRUE on success, FALSE otherwise.
   */
  private function add_dependency_link_from_id($extension_id, $dependency_id)
  {
    if ($this->has_dependency_link($extension_id, $dependency_id))
      return TRUE;
    $query = new SqlQuery('
      INSERT INTO {t_extension_dependency_map}
        (extension_id, dependency_id)
      VALUES
        ({extension_id}, {dependency_id})');
    $query->set_table_names($this->table_names);
    $query->set_int('extension_id',  $extension_id);
    $query->set_int('dependency_id', $dependency_id);
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    return TRUE;
  }


  /// Checks whether the required dependencies are installed.
  /**
   * Returns TRUE if all dependencies needed to install the given
   * extension are installed, FALSE otherwise.
   * \return Boolean.
   */
  public function check_dependencies(SpiffExtension &$extension)
  {
    $dependency_re = '(' . SPIFF_EXTENSION_HANDLE_RE . ')'
                   . '(?:'
                   .    ' ?'
                   .    '(' . SPIFF_EXTENSION_VERSION_OPER_RE . ')'
                   .    ' ?'
                   .    '(' . SPIFF_EXTENSION_VERSION_RE      . ')'
                   . ')?';

    // Walk through the dependency list.
    foreach ($extension->get_dependency_list() as $dependency) {
      // Extract the handle, operator, and version number.
      if (!preg_match('/' . $dependency_re . '/',
                      $dependency,
                      $matches))
        continue;
      $dependency_handle   = $matches[1];
      $dependency_operator = $matches[2];
      $dependency_version  = $matches[3];

      if (!$this->get_extension_from_operator($dependency_handle,
                                              $dependency_operator,
                                              $dependency_version))
        return FALSE;
    }
    // Cool, all dependencies are installed!
    return TRUE;
  }


  /*******************************************************************
   * Handling extensions.
   *******************************************************************/
  /// Register an extension.
  /**
   * Inserts the given SpiffExtension into the database. If the extension is
   * already installed, nothing is done.
   * \return The installed SpiffExtension.
   */
  public function &install_extension(SpiffExtension &$extension)
  {
    // Check whether the extension is already installed.
    if ($this->has_extension($extension))
      return $extension;
    
    // Start transaction.
    $this->db->StartTrans();

    // Make sure that all dependencies are installed.
    if (!$this->check_dependencies($extension))
      die('SpiffExtensionDB:install_extension(): Attempt to install'
          ' an extension with unmatched dependencies.');

    // Insert the extension into the extension table.
    $query = new SqlQuery('
      INSERT INTO {t_extension}
        (handle, name, version, description)
      VALUES
        ({handle}, {name}, {version}, {description})');
    $query->set_table_names($this->table_names);
    $query->set_string('handle',      $extension->get_handle());
    $query->set_string('name',        $extension->get_name());
    $query->set_string('version',     $extension->get_version());
    $query->set_string('description', $extension->get_description());
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    $extension->set_id($this->db->Insert_Id());

    // Walk through all dependencies.
    foreach ($extension->get_dependency_list() as $dependency) {
      // Extract the handle, operator, and version number.
      if (!preg_match('/' . $dependency_re . '/',
                      $dependency,
                      $matches))
        assert('FALSE; // Invalid dependency specifier');
      $dependency_handle   = $matches[1];
      $dependency_operator = $matches[2];
      $dependency_version  = $matches[3];
      
      // Add the requested dependency into the table.
      $query = new SqlQuery('
        INSERT INTO {t_extension_dependency}
          (extension_id,
           dependency_handle,
           dependency_operator,
           dependency_version)
        VALUES
          ({extension_id},
           {dependency_handle},
           {dependency_operator},
           {dependency_version})');
      $query->set_table_names($this->table_names);
      $query->set_int('extension_id', $extension->get_id());
      $query->set_string('dependency_handle',   $dependency_handle);
      $query->set_string('dependency_operator', $dependency_operator);
      $query->set_string('dependency_version',  $dependency_version);
      $rs = $this->db->Execute($query->sql());
      assert('is_object($rs)');

      // And add the best matching dependency into the tree.
      $dependency = $this->get_extension_from_operator($dependency_handle,
                                                       $dependency_operator,
                                                       $dependency_version);
      
      // Retrieve a list of all dependencies of that dependency.
      $dependency_id   = $dependency->get_id();
      $dependency_list = $this->get_dependency_id_list_from_id($dependency_id);
      array_push($dependeny_list, $dependency_id);

      // Add a link to all of the dependencies.
      foreach ($dependency_list as $dependency_id) {
        $this->add_dependency_link_from_id($extension->get_id(),
                                           $dependency_id);
      }
    }

    // Walk through all extensions that currently depend on another
    // version of the recently installed extension.
    $query = new SqlQuery('
      SELECT d.*,m.id
      FROM      {t_extension}            e
      LEFT JOIN {t_extension_dependency} d ON e.id=d.extension_id
      WHERE d.handle={handle}
      AND   d.version!={version}');
    $query->set_table_names($this->table_names);
    $query->set_string('handle',  $extension->get_handle());
    $query->set_string('version', $extension->get_version());
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    while ($row = $rs->FetchRow()) {
      $dependency = $this->get_extension_from_operator($row['handle'],
                                                       $row['operator'],
                                                       $row['version']);

      // No need to do anything if the installed link is already the best one.
      if ($this->has_dependency_link($extension->get_id(), $dependency->get_id())
        continue;

      // Delete the old dependency links.
      $this->delete_dependency_link_from_id($extension->get_id());

      // Retrieve a list of all dependencies of that dependency.
      $dependency_id   = $dependency->get_id();
      $dependency_list = $this->get_dependency_id_list_from_id($dependency_id);
      array_push($dependeny_list, $dependency_id);

      // Add a link to all of the dependencies.
      foreach ($dependency_list as $dependency_id) {
        $this->add_dependency_link_from_id($extension->get_id(),
                                           $dependency_id);
      }
    }

    // End transaction.
    $this->db->CompleteTrans();
    return $extension;
  }


  /// Removes an extension from the database.
  /**
   * Removes the given SpiffExtension from the database. Returns FALSE
   * if the extension did not exist, TRUE otherwise.
   * \return Boolean.
   */
  public function uninstall_extension_from_id($id)
  {
    assert('is_int($id)');
    //FIXME: Uninstall.
    $this->update_dependency_tree();
    return TRUE;
  }


  /// Removes an extension from the database.
  /**
   * Convenience wrapper around uninstall_extension_from_id().
   */
  public function uninstall_extension(SpiffExtension &$extension)
  {
    return uninstall_extension_from_id($extension->get_id());
  }


  /// Checks whether the extension is installed.
  /**
   * Returns TRUE if the given extension is installed with
   * the same version.
   * \return Boolean.
   */
  public function has_extension(SpiffExtension &$extension)
  {
    // Check whether the given extension is installed.
    $query = new SqlQuery('
      SELECT    e.id
      FROM      {t_extension} e
      WHERE e.handle={handle}
      AND   e.version={version}');
    $query->set_table_names($this->table_names);
    $query->set_string('handle',  $extension->get_handle());
    $query->set_string('version', $extension->get_version());
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    $row = $rs->FetchRow();
    return $row ? TRUE : FALSE;
  }


  /// Returns the extension with the given id.
  /**
   */
  public function &get_extension_from_id($id)
  {
    assert('is_int($id)');
    $query = new SqlQuery('
      SELECT    e1.*,e2.handle dep_handle
      FROM      {t_extension}            e1
      LEFT JOIN {t_extension_dependency} d1 ON e1.id=d1.extension_id
      LEFT JOIN {t_extension_dependency} d2 ON d2.lft>d1.lft AND d2.rgt<d1.rgt
      LEFT JOIN {t_extension}            e2 ON e2.id=d2.extension_id
      WHERE e1.id={id}
      ORDER BY d2.lft');
    $query->set_table_names($this->table_names);
    $query->set_int('id', $id);
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    while($row = $rs->FetchRow()) {
      if (!isset($extension)) {
        $extension = new SpiffExtension($row['handle'],
                                        $row['name'],
                                        $row['version'],
                                        $this->acl_section);
        $extension->set_description($row['description']);
      }
      $extension->add_dependency($row['dep_handle']);
    }
    return $extension;
  }


  /// Returns the extension with the given handle and version.
  /**
   */
  public function &get_extension_from_handle($handle, $version)
  {
    assert('isset($handle)');
    assert('isset($version)');
    $query = new SqlQuery('
      SELECT    e1.*,e2.handle dep_handle
      FROM      {t_extension}            e1
      LEFT JOIN {t_extension_dependency} d1 ON e1.id=d1.extension_id
      LEFT JOIN {t_extension_dependency} d2 ON d2.lft>d1.lft AND d2.rgt<d1.rgt
      LEFT JOIN {t_extension}            e2 ON e2.id=d2.extension_id
      WHERE e1.handle={handle}
      AND   e1.version={version}
      ORDER BY d2.lft');
    $query->set_table_names($this->table_names);
    $query->set_string('handle',  $handle);
    $query->set_string('version', $version);
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    while($row = $rs->FetchRow()) {
      if (!isset($extension)) {
        $extension = new SpiffExtension($row['handle'],
                                        $row['name'],
                                        $row['version'],
                                        $this->acl_section);
        $extension->set_description($row['description']);
      }
      $extension->add_dependency($row['dep_handle']);
    }
    return $extension;
  }


  /// Returns the extension that best matches the given criteria.
  /**
   * Returns the extension with the highest version number that matches the
   * given criteria.
   * \param $operator One of '=' or '>='.
   */
  public function &get_extension_from_operator($handle, $operator, $version)
  {
    $installed_versions = $this->get_extension_version_list_from_handle(
                                                                    $handle);

    // Operator '=' is easy...
    if ($operator == '=') {
      $extension = $this->get_extension_from_handle($handle, $version);
      return $extension;
    }

    // Ending up here, the operator is '>='.
    // Select the dependency with the version number that
    // matches the version requirement.
    $best_version = NULL;
    foreach ($installed_versions as $installed_version) {
      if ($this->version_is_greater($installed_version, $version)
        && $this->version_is_greater($installed_version, $best_version))
        $best_version = $installed_version;
    }

    if ($best_version == NULL)
      return FALSE;

    return $this->get_extension_from_handle($handle, $best_version);
  }




  /// Returns a list of all installed versions of an extension.
  /**
   * Returns a list of all installed versions of the extension
   * with the given handle.
   * \return An array of SpiffExtensions.
   */
  public function &get_extension_version_list_from_handle($handle)
  {
    assert('isset($handle) && $handle != ""');
    //FIXME.
    return $version_list;
  }
}
?>
