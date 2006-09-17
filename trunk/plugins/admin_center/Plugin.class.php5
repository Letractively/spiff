<?php
/*
Extension:   Spiff Admin Center
Handle:      spiff_admin
Version:     0.1
Author:      Samuel Abels
Description: This extension brings all administration tasks together.
Depends:     spiff>=0.1 login
*/
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
include_once SPIFF_DIR         . '/actions/printer_base.class.php';
include_once dirname(__FILE__) . '/user_manager_printer.class.php';
include_once dirname(__FILE__) . '/permission_tree_printer.class.php';

class SpiffExtension_spiff_admin extends SpiffExtension {
  private $spiff;

  function initialize(&$spiff) {
    $this->spiff = $spiff;
  }


  public function on_render_request() {
    $smarty = $this->spiff->get_smarty();
    $smarty->template_dir = dirname(__FILE__) . '/templates';

    if (isset($_GET['permission_tree'])) {
      $printer = new PermissionTreePrinter($this->spiff);
      return $printer->show();
    }
    else if (isset($_GET['manage_users'])) {
      $printer = new UserManagerPrinter($this->spiff);
      return $printer->show();
    }
    else
      return $smarty->fetch('admin.tpl');
  }
}
?>
