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
      't_extension' => $this->db_table_prefix . 'extension',
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
}
?>
