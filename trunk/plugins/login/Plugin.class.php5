<?php
/*
Extension:   Login Form
Handle:      login
Version:     0.1
Author:      Samuel Abels
Description: Displays a form for logging in.
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
  private $spiff;
  private $render;
  
  function initialize(&$spiff) {
    $this->spiff = $spiff;
    $bus         = $spiff->get_event_bus();
    $bus->register_callback('on_page_open', array($this, 'on_page_open'));
  }

  public function login($username, $password) {
    if (!isset($username) || !isset($password))
      return FALSE;
    // Get user from database.
    $acldb = $this->spiff->get_acldb();
    $user  = $acldb->get_resource_from_name($username, 'users');
    if (!$user)
      return FALSE;
    $_SESSION['uid'] = $user->get_id();
    return TRUE;
  }

  public function on_page_open() {
    //echo "SpiffExtension_login::on_page_open()<br>\n";
    session_start();
    
    if ($this->spiff->get_current_user() != NULL)
      $this->render = 'nothing';
    else
      $this->render = 'form';

    if (isset($_POST['login'])) {
      if ($this->login($_POST['username'], $_POST['password']))
        $this->render = 'nothing';
      else
        $this->render = 'failure';
    }
  }

  public function on_render_request() {
    //echo "SpiffExtension_login::on_render_request()<br>\n";
    $smarty = $this->spiff->get_smarty();
    $user   = $this->spiff->get_current_user();
    switch ($this->render) {
    case 'nothing':
      $smarty->assign_by_ref('user', $user);
      return $smarty->fetch('logged_in.tpl');
      break;

    case 'form':
      return $smarty->fetch('login.tpl');
      break;

    case 'failure':
      $smarty->assign('error', gettext("Login failed."));
      return $smarty->fetch('login.tpl');
      break;
    }
  }
}
?>
