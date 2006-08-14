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
    function submit_group($gid, $parent_gid) {
      if ($gid != 0)
        $group = $this->gacl->get_actor_group($gid);
      else {
        $parent = $this->gacl->get_actor_group($parent_gid);
        $group  = $this->gacl->add_actor_group($parent, $_POST['name']);
      }
      $group->set_name($_POST['name']);
      $group->set_attribute('description',      $_POST['description']);
      $group->set_attribute('use_group_rights', $_POST['use_group_rights'] ? TRUE : FALSE);
      $this->gacl->save_actor_group($group);
      return $group->get_aro();
    }


    function submit_user($uid, $parent_gid) {
      if ($uid != 0) {
        $user = $this->gacl->get_actor($uid);
        $user->set_name($_POST['name']);
      }
      else {
        $section = new GaclActorSection('Users', NULL);
        $user    = $this->gacl->add_actor($_POST['name'], $section);
        $parent  = $this->gacl->get_actor_group($parent_gid);
        $group   = $this->gacl->assign_actor_to_group($user, $parent);
      }
      $user->set_attribute('description',      $_POST['description']);
      $user->set_attribute('use_group_rights', $_POST['use_group_rights'] ? TRUE : FALSE);
      $this->gacl->save_actor($user);
      return $user->get_aro();
    }


    function show_group($gid, $parent_gid) {
      if ($gid != 0)
        $group = $this->gacl->get_actor_group($gid);
      else
        $group = new GaclActorGroup('', NULL);
      $groups     = phpgacl_get_group_list($this->gacl->gacl, $gid);
      $users      = $this->gacl->get_actor_list($group);
      $may_admin  = phpgacl_get_group_permission_list($this->gacl->gacl,
                                                      $gid,
                                                      'users',
                                                      'administer');
      $may_create = phpgacl_get_group_permission_list($this->gacl->gacl,
                                                      $gid,
                                                      'users',
                                                      'create');
      $may_edit   = phpgacl_get_group_permission_list($this->gacl->gacl,
                                                      $gid,
                                                      'users',
                                                      'edit');
      $may_delete = phpgacl_get_group_permission_list($this->gacl->gacl,
                                                      $gid,
                                                      'users',
                                                      'delete');
      $this->smarty->clear_all_assign();
      $this->smarty->assign_by_ref('groups',     $groups);
      $this->smarty->assign_by_ref('users',      $users);
      $this->smarty->assign_by_ref('group',      $group);
      $this->smarty->assign_by_ref('parent_gid', $parent_gid);
      $this->smarty->assign_by_ref('may_admin',  $may_admin);
      $this->smarty->assign_by_ref('may_create', $may_create);
      $this->smarty->assign_by_ref('may_edit',   $may_edit);
      $this->smarty->assign_by_ref('may_delete', $may_delete);
      $this->parent->append_content($this->smarty->fetch('group_editor.tpl'));
    }


    function add_group($parent_gid) {
      $this->show_group(0, $parent_gid);
    }


    function delete_group($gid, $parent_gid) {
      $group = $this->gacl->get_actor_group($gid);
      $this->gacl->delete_actor_group($group);
      $this->show_group($parent_gid, $parent_gid);
    }


    function show_user($uid, $parent_gid) {
      if ($uid != 0)
        $user = $this->gacl->get_actor($uid);
      else
        $user = new GaclActor('', new GaclActorSection('users', NULL), NULL);
      $may_admin  = phpgacl_get_user_permission_list($this->gacl->gacl,
                                                     $uid,
                                                     'users',
                                                     'administer');
      $may_create = phpgacl_get_user_permission_list($this->gacl->gacl,
                                                     $uid,
                                                     'users',
                                                     'create');
      $may_edit   = phpgacl_get_user_permission_list($this->gacl->gacl,
                                                     $uid,
                                                     'users',
                                                     'edit');
      $may_delete = phpgacl_get_user_permission_list($this->gacl->gacl,
                                                     $uid,
                                                     'users',
                                                     'delete');
      $this->smarty->clear_all_assign();
      $this->smarty->assign_by_ref('user',       $user);
      $this->smarty->assign_by_ref('parent_gid', $parent_gid);
      $this->smarty->assign_by_ref('may_admin',  $may_admin);
      $this->smarty->assign_by_ref('may_create', $may_create);
      $this->smarty->assign_by_ref('may_edit',   $may_edit);
      $this->smarty->assign_by_ref('may_delete', $may_delete);
      $this->parent->append_content($this->smarty->fetch('user_editor.tpl'));
    }


    function add_user($parent_gid) {
      $this->show_user(0, $parent_gid);
    }


    function delete_user($uid, $parent_gid) {
      $user = $this->gacl->get_actor($uid);
      $this->gacl->delete_actor($user);
      $this->show_group($parent_gid, $parent_gid);
    }


    function show() {
      if (isset($_GET['parent_gid']))
        $parent_gid = $_GET['parent_gid'] * 1;
      if (!isset($_GET['gid']) && !isset($_GET['uid'])) {
        $gid        = $this->gacl->gacl->get_group_id('everybody');
        $parent_gid = $gid;
      }
      elseif (isset($_GET['gid']))
        $gid = $_GET['gid'] * 1;
      elseif (isset($_GET['uid']))
        $uid = $_GET['uid'] * 1;

      if (isset($_POST['save']) && isset($gid)) {
        $gid = $this->submit_group($gid, $parent_gid);
        $this->show_group($gid, $parent_gid);
      }
      elseif (isset($_POST['save']) && isset($uid)) {
        $uid = $this->submit_user($uid, $parent_gid);
        $this->show_user($uid, $parent_gid);
      }
      elseif (isset($_POST['delete']) && isset($gid))
        $this->delete_group($gid, $parent_gid);
      elseif (isset($_POST['delete']) && isset($uid))
        $this->delete_user($uid, $parent_gid);
      elseif (isset($_POST['group_add']) && isset($gid))
        $this->add_group($gid);
      elseif (isset($_POST['user_add']) && isset($gid))
        $this->add_user($gid);
      elseif (isset($gid))
        $this->show_group($gid, $parent_gid);
      elseif (isset($uid))
        $this->show_user($uid, $parent_gid);
    }
  }
?>
