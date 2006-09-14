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
include_once dirname(__FILE__).'/SpiffExtensionDB.class.php5';
include_once dirname(__FILE__).'/../libuseful/zip.inc.php';

class SpiffExtensionStore {
  private $extension_db;
  private $directory;
  private $event_bus;
  
  function __construct(&$db, $directory)
  {
    assert('is_object($db)');
    assert('is_dir($directory)');
    $this->extension_db = &new SpiffExtensionDB($db);
    $this->directory    = $directory;
    $this->event_bus    = &new EventBus();
  }


  /*******************************************************************
   * Private helper functions.
   *******************************************************************/


  /*******************************************************************
   * General behavior.
   *******************************************************************/
  /// Turns debugging messages on/off.
  /**
   * Turns debugging on if TRUE is given, or off if FALSE is given.
   */
  public function debug($debug = TRUE)
  {
    $this->db->debug = $debug;
  }


  public function install()
  {
    return $this->extension_db->install();
  }


  public function clear_database()
  {
    return $this->extension_db->clear_database();
  }


  public function set_table_prefix($prefix)
  {
    return $this->extension_db->set_table_prefix($prefix);
  }


  /// Defines the directory in which extensions are installed.
  /**
   */
  public function set_directory($directory)
  {
    assert('is_dir($directory)');
    $this->directory = $directory;
  }


  public function get_event_bus()
  {
    return $this->event_bus;
  }


  /*******************************************************************
   * Parser.
   *******************************************************************/
  /// Extracts the relevant information from the header of the given file.
  /**
   * \return The extracted information in an associative array, or NULL.
   */
  private function parse_file($filename)
  {
    $tags   = '(?:Extension|Handle|Version|Author|Description|Depends)';
    $tag    = '';
    $fp     = fopen($filename, 'r');
    $header = array();
    fgets($fp);
    fgets($fp);
    while ($line = fgets($fp)) {
      // End of header.
      if (preg_match('/^\s*\*\/$/', $line))
        break;

      // Followup value.
      if (isset($tag) && preg_match('/^\s+(.*)$/', $line, $matches))
        $header[$tag] .= ' ' . $matches[1];

      // New tag.
      if (!preg_match("/^($tags):\s+(.*)$/", $line, $matches))
        continue;
      $tag          = strtolower($matches[1]);
      $header[$tag] = $matches[2];
      //print "Tag: $tag, Value: $header[$tag]<br>";
    }

    if (!isset($header['extension'])
      || !isset($header['handle'])
      || !isset($header['version'])
      || !isset($header['author'])
      || !isset($header['description'])
      || !isset($header['depends']))
      return NULL;

    $header['depends'] = split(' *, *', $header['depends']);
    return $header;
  }


  /// Extracts the given archive into a temporary directory.
  /**
   * \return The name of the temporary directory, or NULL.
   */
  private function install_archive($filename)
  {
    //FIXME: Make sure theres no name collision with the destination directory.
    $temp_dir = '';
    if (!unzip($filename, $temp_dir))
      return NULL;
    return $temp_dir;
  }


  /*******************************************************************
   * Installer.
   *******************************************************************/
  /// Installs the extension with the given filename.
  /**
   * May be given the name of an archive file, or the name of a directory
   * containing the extracted extension.
   * \return -1 if the archive was not found.
   *         -2 if the archive could not be unpacked.
   *         -3 if Plugin.class.php5 is missing.
   *         -4 if the header could not be parsed correctly.
   *         -5 if the class could not be instantiated.
   *         -6 if the dependencies could not be solved.
   *         -7 if the extension could not be installed.
   *         -8 if the extension could not be registered.
   *         The SpiffExtension class on success.
   */
  public function add_extension($filename)
  {
    if (!file_exists($filename))
      return -1;
    if (is_dir($filename))
      $temp_dir = $filename;
    else if (!$temp_dir = $this->install_archive($filename))
      return -2;
    $filename = $temp_dir . '/Plugin.class.php5';
    if (!file_exists($filename))
      return -3;
    $header = $this->parse_file($filename);
    if (!is_array($header))
      return -4;

    // Instantiate the extension.
    include_once $temp_dir . '/Plugin.class.php5';
    $classname = 'SpiffExtension_' . $header['handle'];
    $extension = new $classname($header['handle'],
                                $header['extension'],
                                $header['version']);
    if (!is_object($extension))
      return -5;
    $extension->set_author($header['author']);
    $extension->set_description($header['description']);
    foreach ($header['depends'] as $depend)
      $extension->add_dependency($depend);

    // Checks.
    if (!$this->extension_db->check_dependencies($extension))
      return -6;

    // Ok, so the extension seems to be fine. Install it in the
    // final directory.
    if (!rename($temp_dir, $this->directory))
      return -7;

    // Register it.
    if (!$this->extension_db->register_extension($extension))
      return -8;
    return $extension;
  }
}
?>
