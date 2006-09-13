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

class SpiffExtensionStore {
  private $extension_db;
  
  function __construct(&$db)
  {
    assert('is_object($db)');
    $this->extension_db = new SpiffExtensionDB($db);
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
    }

    if (isset($header['extension'])
      || !isset($header['handle'])
      || !isset($header['version'])
      || !isset($header['author'])
      || !isset($header['description'])
      || !isset($header['depends'])) {
      echo "Incomplete extension header in '$filename'.";
      return NULL;
    }

    $header['depends'] = split(' *, *', $header['depends']);
    return $header;
  }


  /*******************************************************************
   * Installer.
   *******************************************************************/
  public function add_extension($filename)
  {
    $header = $this->parse_file($filename);
    assert('$extension != NULL');

    // Instantiate the extension.
    $classname = 'SpiffExtension_' . $header['handle'];
    $extension = new $classname($header['handle'],
                                $header['extension'],
                                $header['version']);
    $extension->set_author($header['author']);
    $extension->set_description($header['description']);
    foreach ($header['depends'] as $depend)
      $extension->add_dependency($depend);

    // Check & install.
    if (!$this->extension_db->check_dependencies($extension))
      return NULL;
    $this->extension_db->register_extension($extension);
    return $extension;
  }
}
?>
