<?php
  /*
  Copyright (C) 2003 Samuel Abels, <spam debain org>

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
  class UserManagerPrinter extends PrinterBase {
    function show_group($gid) {
      // Get the group info from phpgacl, joined with the group attributes.
      $group      = phpgacl_get_group_info($this->gacl, $gid);
      $groups     = phpgacl_get_group_list($this->gacl, $gid);
      $users      = phpgacl_get_user_list($this->gacl, $gid);
      $may_admin  = phpgacl_get_group_permission_list($this->gacl,
                                                      $gid,
                                                      'users',
                                                      'administrate');
      $may_create = phpgacl_get_group_permission_list($this->gacl,
                                                      $gid,
                                                      'users',
                                                      'create');
      $may_edit   = phpgacl_get_group_permission_list($this->gacl,
                                                      $gid,
                                                      'users',
                                                      'edit');
      $may_delete = phpgacl_get_group_permission_list($this->gacl,
                                                      $gid,
                                                      'users',
                                                      'delete');

      $this->smarty->clear_all_assign();
      $this->smarty->assign_by_ref('groups',     $groups);
      $this->smarty->assign_by_ref('users',      $users);
      $this->smarty->assign_by_ref('group',      $group);
      $this->smarty->assign_by_ref('may_admin',  $may_admin);
      $this->smarty->assign_by_ref('may_create', $may_create);
      $this->smarty->assign_by_ref('may_edit',   $may_edit);
      $this->smarty->assign_by_ref('may_delete', $may_delete);
      $this->parent->append_content($this->smarty->fetch('group_editor.tpl'));
    }


    function show_user($uid) {
      // Get the user info from phpgacl, joined with the user attributes.
      $user       = phpgacl_get_user_info($this->gacl, $uid);
      $may_admin  = phpgacl_get_user_permission_list($this->gacl,
                                                     $uid,
                                                     'users',
                                                     'administrate');
      $may_create = phpgacl_get_user_permission_list($this->gacl,
                                                     $uid,
                                                     'users',
                                                     'create');
      $may_edit   = phpgacl_get_user_permission_list($this->gacl,
                                                     $uid,
                                                     'users',
                                                     'edit');
      $may_delete = phpgacl_get_user_permission_list($this->gacl,
                                                     $uid,
                                                     'users',
                                                     'delete');

      $this->smarty->clear_all_assign();
      $this->smarty->assign_by_ref('user',       $user);
      $this->smarty->assign_by_ref('may_admin',  $may_admin);
      $this->smarty->assign_by_ref('may_create', $may_create);
      $this->smarty->assign_by_ref('may_edit',   $may_edit);
      $this->smarty->assign_by_ref('may_delete', $may_delete);
      $this->parent->append_content($this->smarty->fetch('user_editor.tpl'));
    }


    function show() {
      if (!isset($_GET['gid']) && !isset($_GET['uid']))
        $gid = $this->gacl->get_group_id('everybody');
      elseif (isset($_GET['gid']))
        $gid = $_GET['gid'] * 1;
      elseif (isset($_GET['uid']))
        $uid = $_GET['uid'] * 1;

      if (isset($gid))
        $this->show_group($gid);
      elseif (isset($uid))
        $this->show_user($uid);
    }
  }
?>
