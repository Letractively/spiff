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
  class PermissionTreePrinter extends PrinterBase {
    function show_tree($actor_id, $actor_gid, $resource_gid) {
      assert('$actor_id || $actor_gid');

      // Get resource information.
      if ($resource_gid)
        $resource_group = $this->gacl->get_resource_group($resource_gid);

      if (isset($resource_group)
        && $resource_group->get_name() != 'Root') {
        // Get a list of all users and groups under the given group id.
        $resource_group_list = $this->gacl->get_resource_group_list($resource_group);
        $resource_list       = $this->gacl->get_resource_list($resource_group);
        $parent_group        = $this->gacl->get_resource_group_parent($resource_group);
      }
      else {
        $everybody_gid       = $this->gacl->get_resource_group_id_from_name('Everybody');
        $resource_group      = $this->gacl->get_resource_group($everybody_gid);
        $resource_group_list = array($resource_group);
        $resource_list       = array();
      }

      // Because phpgacl sucks, we need to handle groups and users (actors)
      // separately.
      // Get the permission list if the currently edited item is an actor.
      if ($actor_id) {
        $actor = $this->gacl->get_actor($actor_id);

        // Receive a list of permissions of each of the groups found.
        $groups = array();
        foreach ($resource_group_list as $current) {
          $perms = $this->gacl->get_actor_resource_group_permissions($actor,
                                                                     $current);
          $current->permission = $perms;
          array_push($groups, $current);
        }

        // Receive a list of permissions of each of the users found.
        $users = array();
        foreach ($resource_list as $current) {
          $perms = $this->gacl->get_actor_resource_permissions($actor,
                                                               $current);
          $current->permission = $perms;
          array_push($users, $current);
        }
      }

      // Get the permission list if the currently edited item is a group.
      if ($actor_gid) {
        $actor_group = $this->gacl->get_actor_group($actor_gid);

        // Receive a list of permissions of each of the groups found.
        $groups = array();
        foreach ($resource_group_list as $current) {
          $perms = $this->gacl->get_actor_group_resource_group_permissions(
                                                       $actor_group, $current);
          $current->permission = $perms;
          array_push($groups, $current);
        }

        // Receive a list of permissions of each of the users found.
        $users = array();
        foreach ($resource_list as $current) {
          $perms = $this->gacl->get_actor_group_resource_permissions(
                                                       $actor_group, $current);
          $current->permission = $perms;
          array_push($users, $current);
        }
      }

      // Fire smarty.
      $this->smarty->clear_all_assign();
      if (isset($parent_group))
        $this->smarty->assign('parent', $parent_group);
      $this->smarty->assign('actor_id',  $actor_id);
      $this->smarty->assign('actor_gid', $actor_gid);
      $this->smarty->assign_by_ref('groups', $groups);
      $this->smarty->assign_by_ref('users',  $users);
      $this->parent->append_content($this->smarty->fetch('permission_tree.tpl'));
    }


    function show() {
      $actor_id  = '';
      $actor_gid = '';
      if (isset($_GET['actor_id']))
        $actor_id = $_GET['actor_id'] * 1;
      else if (isset($_GET['actor_gid']))
        $actor_gid = $_GET['actor_gid'] * 1;
      else
        die("PermissionTreePrinter::show(): Actor id missing");
      if (isset($_GET['resource_gid']))
        $resource_gid = $_GET['resource_gid'] * 1;
      else
        $resource_gid = '';
      $this->show_tree($actor_id, $actor_gid, $resource_gid);
    }
  }
?>
