<?php
/*
Extension:   Login Form
Handle:      login
Version:     0.1
Author:      Samuel Abels
Description: Demo plugin to shows how it works.
Depends:     spiff
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
class SpiffExtension_login extends SpiffExtension {
  function initialize() {
    $this->register_callback('on_page_open',
                             '$this->on_page_open');
    $this->register_callback('on_render_request',
                             '$this->on_render_request');
  }

  public function on_page_open() {
    echo "SpiffExtension_login::on_page_open()<br>\n";
  }

  public function on_render_request() {
    echo "SpiffExtension_login::on_render_request()<br>\n";
    $this->append_content($this->smarty->fetch('login.tpl'));
  }
}
?>
