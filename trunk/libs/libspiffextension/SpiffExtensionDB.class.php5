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
  
  function __contructor(SpiffAclDB &$acldb)
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
      't_extension'            => $this->db_table_prefix . 'extension',
      't_extension_dependency' => $this->db_table_prefix . 'extension_dependency'
    );
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
   * Handling dependencies.
   *******************************************************************/
  /// Links the given extension with the given dependency.
  /**
   * Links the extension with the given id with the dependency with
   * the given id.
   * \return TRUE  on success, FALSE otherwise.
   */
  private function add_dependency_from_id($extension_id, $dependency_id)
  {
    //FIXME.
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
    // Walk through the dependency list.
    foreach ($extension->get_dependency_list() as $dependency) {
      // Find all installed versions of the dependency.
      $versions = $this->get_extension_version_list_from_handle($dependency);

      // Select the dependency with the highest version number that
      // matches the version requirement.
      unset($best_dependency);
      foreach ($versions as $dependency_version) {
        //FIXME
      }

      // If no matching dependency exists, return FALSE.
      if (!isset($best_dependency))
        return FALSE.
    }
    // Cool, all dependencies are installed!
    return TRUE;
  }


  /*******************************************************************
   * Handling extensions.
   *******************************************************************/
  /// Checks whether the extension is installed.
  /**
   * Returns TRUE if the given extension is installed with
   * the same version.
   * \return Boolean.
   */
  public function has_extension(SpiffExtension &$extension)
  {
    // Check whether the given extension is installed.
    //FIXME
    return TRUE;
  }


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
    //FIXME.

    // Walk through all dependencies.
    foreach ($extension->get_dependency_list() as $dependency) {
      // Find all installed versions of the dependency.
      $versions = $this->get_extension_version_list_from_handle($dependency);
      
      // Select the dependency with the highest version number that
      // matches the version requirement.
      unset($best_dependency);
      foreach ($version as $dependency_version) {
        //FIXME
      }
      
      // If no matching dependency exists, something was really
      // broken.
      if (!isset($best_dependency))
        die('SpiffExtensionDB:install_extension(): Argh! No matching'
            ' dependency found - something must be really broken.');

      // Link the extension with the best dependency in the tree.
      $this->add_dependency_from_id($extension_id,
                                    $best_dependency_id);
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
    //FIXME.
  }


  /// Removes an extension from the database.
  /**
   * Convenience wrapper around uninstall_extension_from_id().
   */
  public function uninstall_extension(SpiffExtension &$extension)
  {
    return uninstall_extension_from_id($extension->get_id());
  }


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


  /// Returns a list of all installed versions of an extension.
  /**
   * Returns a list of all installed versions of the extension
   * with the given handle.
   * \return An array of SpiffExtensions.
   */
  private function get_extension_version_list_from_handle($handle)
  {
    assert('isset($handle) && $handle != ""');
    //FIXME.
    return $version_list;
  }
}
?>
