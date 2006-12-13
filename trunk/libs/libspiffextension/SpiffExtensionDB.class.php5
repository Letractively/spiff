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
  private $db;
  private $db_table_prefix;
  private $acl_section_handle;
  
  function __construct(&$acldb, $acl_section_handle = 'extensions')
  {
    assert('is_object($acldb)');
    assert('isset($acl_section_handle)');
    $this->acldb           = $acldb;
    $this->db              = $acldb->db;
    $this->db_table_prefix = '';
    $this->acl_section     = &new SpiffAclResourceSection($acl_section_handle);
    $this->update_table_names();
  }


  /*******************************************************************
   * Private helper functions.
   *******************************************************************/
  private function update_table_names()
  {
    $this->table_names = array (
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
    assert('isset($version_a)');
    assert('isset($version_b)');
    // Split the version string into the components separated by dots.
    $a_numbers = explode('.', $version_a);
    $b_numbers = explode('.', $version_b);

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

      // The current registered version number has to be greater or equal.
      if ($a_numbers[$i] < $b_numbers[$i])
        return FALSE;
    }

    return TRUE;
  }


  /*******************************************************************
   * General behavior.
   *******************************************************************/
  /// Installs all database tables that are required by libspiffextension.
  /**
   * Returns TRUE on success, FALSE otherwise.
   */
  public function install()
  {
    $schema = new adoSchema($this->db);
    $schema->SetPrefix($this->db_table_prefix);
    $sql = $schema->ParseSchema(dirname(__FILE__) . '/schema.xml');
    //print_r($sql);
    if ($schema->ExecuteSchema() != 2)
      return FALSE;
    return TRUE;
  }


  /// Clears out the entire database. Use with care.
  /**
   * Wipes out everything.
   */
  public function clear_database()
  {
    return $this->acldb->clear_section($this->acl_section);
  }


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
    assert('isset($extension_id)');
    assert('isset($dependency_id)');
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
    //$this->debug();
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    return TRUE;
  }


  /// Checks whether the required dependencies are registered.
  /**
   * Returns TRUE if all dependencies needed to register the given
   * extension are registered, FALSE otherwise.
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
      $dependency_operator = isset($matches[2]) ? $matches[2] : '>=';
      $dependency_version  = isset($matches[3]) ? $matches[3] : 0;

      if (!$this->get_extension_from_operator($dependency_handle,
                                              $dependency_operator,
                                              $dependency_version))
        return FALSE;
    }
    // Cool, all dependencies are registered!
    return TRUE;
  }


  /*******************************************************************
   * Handling extensions.
   *******************************************************************/
  /// Register an extension.
  /**
   * Inserts the given SpiffExtension into the database. If the extension is
   * already registered, nothing is done.
   * \return The registered SpiffExtension.
   */
  public function &register_extension(SpiffExtension &$extension)
  {
    // Check whether the extension is already registered.
    if ($this->get_extension_from_handle($extension->get_handle(),
                                         $extension->get_version()))
      return $extension;
    
    // Start transaction.
    //$this->debug();
    //echo "Installing " . $extension->get_handle() . "<br>\n";
    $this->db->StartTrans();

    // Make sure that all dependencies are registered.
    if (!$this->check_dependencies($extension))
      die('SpiffExtensionDB:register_extension(): Attempt to register'
         .' an extension with unmatched dependencies.');

    // Create a group that holds all versions of the extension.
    $handle         = $extension->get_handle();
    $section_handle = $this->acl_section->get_handle();
    if ($this->acldb->get_resource_from_handle($handle, $section_handle))
      $parent = $this->acldb->get_resource_from_handle($handle);
    else {
      $parent = new SpiffAclResourceGroup($extension->get_name(), $handle);
      $parent = $this->acldb->add_resource(NULL, $parent, $this->acl_section);
    }

    // Insert the extension into the ACL resource table.
    $old_handle = $extension->get_handle();
    $handle     = libspiffacl_mkhandle_from_string($extension->get_handle()
                                                .$extension->get_version());
    $extension->set_handle($handle);
    $this->acldb->add_resource($parent->get_id(),
                               $extension,
                               $this->acl_section);
    $extension->set_handle($old_handle);

    $dependency_re = '(' . SPIFF_EXTENSION_HANDLE_RE . ')'
                   . '(?:'
                   .    ' ?'
                   .    '(' . SPIFF_EXTENSION_VERSION_OPER_RE . ')'
                   .    ' ?'
                   .    '(' . SPIFF_EXTENSION_VERSION_RE      . ')'
                   . ')?';

    // Walk through all dependencies.
    foreach ($extension->get_dependency_list() as $dependency) {
      // Extract the handle, operator, and version number.
      if (!preg_match('/' . $dependency_re . '/',
                      $dependency,
                      $matches))
        assert('FALSE; // Invalid dependency specifier');
      $dependency_handle   = $matches[1];
      $dependency_operator = isset($matches[2]) ? $matches[2] : '>=';
      $dependency_version  = isset($matches[3]) ? $matches[3] : 0;
      
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
      //$this->debug();
      $rs = $this->db->Execute($query->sql());
      assert('is_object($rs)');

      // And add the best matching dependency into the tree.
      $dependency = $this->get_extension_from_operator($dependency_handle,
                                                       $dependency_operator,
                                                       $dependency_version);
      
      // Retrieve a list of all dependencies of that dependency.
      $dependency_id   = $dependency->get_id();
      $dependency_list = $this->get_dependency_id_list_from_id($dependency_id);
      //print_r($dependency_list);
      array_push($dependency_list, $dependency_id);

      // Add a link to all of the dependencies.
      foreach ($dependency_list as $dependency_id) {
        $this->add_dependency_link_from_id($extension->get_id(),
                                           $dependency_id);
      }
    }

    // Walk through all extensions that currently depend on another
    // version of the recently registered extension.
    $query = new SqlQuery('
      SELECT d.*
      FROM {t_extension_dependency} d
      WHERE d.dependency_handle={handle}
      AND   d.dependency_version!={version}');
    $query->set_table_names($this->table_names);
    $query->set_string('handle',  $extension->get_handle());
    $query->set_string('version', $extension->get_version());
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    while ($row = $rs->FetchRow()) {
      //print "Found row.<br>";
      $dependency = $this->get_extension_from_operator($row['handle'],
                                                       $row['operator'],
                                                       $row['version']);

      // No need to do anything if the registered link is already the best one.
      if ($this->has_dependency_link($extension->get_id(), $dependency->get_id()))
        continue;

      // Delete the old dependency links.
      $this->delete_dependency_link_from_id($extension->get_id());

      // Retrieve a list of all dependencies of that dependency.
      $dependency_id   = $dependency->get_id();
      $dependency_list = $this->get_dependency_id_list_from_id($dependency_id);
      array_push($dependency_list, $dependency_id);

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
  public function unregister_extension_from_id($id)
  {
    assert('is_int($id)');
    $this->acldb->delete_resource_from_id($id);

    //FIXME: Unregister all extensions that require this extension.
    return TRUE;
  }


  /// Removes an extension from the database.
  /**
   * Convenience wrapper around unregister_extension_from_id().
   */
  public function unregister_extension(SpiffExtension &$extension)
  {
    return unregister_extension_from_id($extension->get_id());
  }


  /// Returns the extension with the given id.
  /**
   */
  public function &get_extension_from_id($id)
  {
    assert('is_int($id)');
    $extension = $this->acldb->get_resource_from_id($id, 'SpiffExtension');
    // Attach a list of dependencies.
    $this->extension_load_dependency_list($extension);
    return $extension;
  }


  /// Attaches a list of dependencies.
  private function extension_load_dependency_list(SpiffExtension &$extension)
  {
    assert('is_object($extension)');
    $query = new SqlQuery('
      SELECT d.dependency_handle
           , d.dependency_operator
           , d.dependency_version
      FROM  {t_extension_dependency} d
      WHERE d.extension_id={id}');
    $query->set_table_names($this->table_names);
    $query->set_int('id', $extension->get_id());
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    while ($row = $rs->FetchRow())
      $extension->add_dependency($row['dependency_handle']
                                .$row['dependency_operator']
                                .$row['dependency_version']);
  }


  /// Returns the extension with the given handle and version.
  /**
   */
  public function &get_extension_from_handle($handle, $version)
  {
    assert('isset($handle)');
    assert('isset($version)');
    $version_handle = libspiffacl_mkhandle_from_string($handle . $version);
    $section_handle = $this->acl_section->get_handle();
    $extension = $this->acldb->get_resource_from_handle($version_handle,
                                                        $section_handle,
                                                        'SpiffExtension');
    if (!$extension) {
      $null = NULL;
      return $null;
    }
    $extension->set_handle($handle);
    $this->extension_load_dependency_list($extension);
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
    assert('isset($handle)');
    assert('isset($operator)');
    assert('isset($version)');

    // Operator '=' is easy...
    if ($operator == '=') {
      $section_handle = $this->acl_section->get_handle();
      $extension = $this->get_extension_from_handle($handle, $version);
      return $extension;
    }

    $versions = $this->get_extension_version_list_from_handle($handle);

    // Ending up here, the operator is '>='.
    // Select the dependency with the version number that
    // matches the version requirement.
    $best_version = '0';
    foreach ($versions as $cur) {
      if ($this->version_is_greater($cur->get_version(), $version)
        && (!$best_version
            || $this->version_is_greater($cur->get_version(),
                                     $best_version->get_version())))
        $best_version = $cur;
    }

    if ($best_version->get_version() == '0') {
      $null = NULL;
      return $null;
    }

    $best_version->set_handle($handle);
    return $best_version;
  }


  /// Returns the extension that best matches the given criteria.
  /**
   * Returns the extension with the highest version number that matches the
   * given criteria.
   * \param $operator One of '=' or '>='.
   */
  public function &get_extension_from_operator_string($specifier)
  {
    assert('isset($specifier)');
    $extension_re = '(' . SPIFF_EXTENSION_HANDLE_RE . ')'
                  . '(?:'
                  .    ' ?'
                  .    '(' . SPIFF_EXTENSION_VERSION_OPER_RE . ')'
                  .    ' ?'
                  .    '(' . SPIFF_EXTENSION_VERSION_RE      . ')'
                  . ')?';

    // Extract the handle, operator, and version number.
    if (!preg_match('/' . $extension_re . '/', $specifier, $matches))
      assert('FALSE; // Invalid extension specifier');
    $handle   = $matches[1];
    $operator = isset($matches[2]) ? $matches[2] : '>=';
    $version  = isset($matches[3]) ? $matches[3] : 0;
    assert('isset($handle)');
    assert('isset($operator)');
    assert('isset($version)');

    return $this->get_extension_from_operator($handle, $operator, $version);
  }


  /// Returns a list of all registered versions of an extension.
  /**
   * Returns a list of all registered versions of the extension
   * with the given handle.
   * \return An array of SpiffExtensions.
   */
  public function &get_extension_version_list_from_handle($handle)
  {
    assert('isset($handle) && $handle != ""');
    $section_handle = $this->acl_section->get_handle();
    $parent   = $this->acldb->get_resource_from_handle($handle,
                                                       $section_handle);
    $versions = $this->acldb->get_resource_children_from_id($parent->get_id(),
                                                            'SpiffExtension');
    return $versions;
  }


  public function &get_dependency_id_list_from_id($extension_id)
  {
    assert('isset($extension_id)');
    $query = new SqlQuery('
      SELECT m.dependency_id
      FROM      {t_extension_dependency_map} m WHERE m.extension_id={id}');
    $query->set_table_names($this->table_names);
    $query->set_int('id', $extension_id);
    $rs = $this->db->Execute($query->sql());
    assert('is_object($rs)');
    $dependency_list = array();
    while ($row = $rs->FetchRow())
      array_push($dependency_list, $row['dependency_id']);
    return $dependency_list;
  }
}
?>