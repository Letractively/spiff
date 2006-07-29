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
    function show() {
      $gid      = $this->gacl->get_group_id('everybody');
      $groupids = $this->gacl->get_group_children($gid);
      $objects  = $this->gacl->get_group_objects($gid);
      $groups   = array();
      $users    = array();
      foreach ($groupids as $gid) {
        $data = $this->gacl->get_group_data($gid);
        $groups[$gid] = $data[3];
      }
      if (isset($objects['users'])) {
        foreach ($objects['users'] as $alias) {
          $uid  = $this->gacl->get_object_id('users', $alias, 'ARO');
          $data = $this->gacl->get_object_data($uid, 'ARO');
          $users[$uid] = $data[0][3];
        }
      }
      $this->smarty->clear_all_assign();
      $this->smarty->assign_by_ref('groups', $groups);
      $this->smarty->assign_by_ref('users',  $users);
      $this->parent->append_content($this->smarty->fetch('usermanager.tpl'));
    }
  }

  $gacl = new gacl_api();
  $gacl->clear_database() or die('Unable to clear db.');

  // Create main sections.
  $gacl->add_object_section('Content', 'content', 10, FALSE, 'AXO')
           or die('Section "Content" failed.');
  $gacl->add_object_section('Users', 'users', 10, FALSE, 'ARO')
           or die('Section "Users" failed.');

  // Add homepage objects.
  $gacl->add_object('content', 'Homepage', 'homepage', 10, FALSE, 'AXO')
           or die('Homepage AXO creation for "view" failed.');

  // Create groups.
  $content_gid = $gacl->add_group('content', 'Content', 0, 'AXO')
           or die('Content group AXO creation failure.');
  $everybody_gid = $gacl->add_group('everybody', 'Everybody', 0, 'ARO')
           or die('"Everybody" user group ARO creation failure.');
  $admin_gid = $gacl->add_group('administrators', 'Administrators', $everybody_gid, 'ARO')
           or die('Root user group ARO creation failure.');
  $user_gid = $gacl->add_group('users', 'Users', $everybody_gid, 'ARO')
           or die('User group ARO creation failure.');

  // Add users into groups.
  $gacl->add_object('users', 'Administrator', 'administrator', 10, FALSE, 'ARO')
           or die('Root user ARO creation failure.');
  $gacl->add_group_object($admin_gid, 'users', 'administrator', 'ARO')
           or die('Root user assign failure.');
  $gacl->add_object('users', 'Anonymous George', 'anonymous', 10, FALSE, 'ARO')
           or die('Anonymous user ARO creation failure.');
  $gacl->add_group_object($user_gid, 'users', 'anonymous', 'ARO')
           or die('Anonymous user assign failure.');
?>
