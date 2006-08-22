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
    function show_tree($actor_id, $resource_id) {
      assert('$actor_id');

      // Get resource information.
      if ($resource_id) {
        // Get a list of all resources under the given group id.
        $resource = $this->acldb->get_resource_from_id($resource_id);
        $groups   = $this->acldb->get_resource_children($resource,
                                                        ACLDB_FETCH_GROUPS);
        $items    = $this->acldb->get_resource_children($resource,
                                                        ACLDB_FETCH_ITEMS);
        $parents  = $this->acldb->get_resource_parents($resource);
      }
      else {
        $section  = new AclResourceSection('users', '');
        $resource = $this->acldb->get_resource_from_handle('everybody',
                                                           $section);
        $groups   = array($resource);
        $items    = array();
        $parent   = NULL;
      }

      // Get the permission list if the currently edited item is an actor.
      $actor = $this->acldb->get_resource_from_id($actor_id);

      // Receive a list of permissions of each of the groups found.
      $group_list = array();
      foreach ($groups as $current) {
        $perms = $this->acldb->get_permission_list($actor, $current);
        $current->permission = $perms;
        array_push($group_list, $current);
      }

      // Receive a list of permissions of each of the users found.
      $item_list = array();
      foreach ($items as $current) {
        $perms = $this->acldb->get_permission_list($actor, $current);
        $current->permission = $perms;
        array_push($item_list, $current);
      }
      //print_r($group_list);
      //print_r($item_list);

      // Fire smarty.
      $this->smarty->clear_all_assign();
      $this->smarty->assign('actor_id', $actor_id);
      $this->smarty->assign_by_ref('parents', $parents);
      $this->smarty->assign_by_ref('groups',  $group_list);
      $this->smarty->assign_by_ref('items',   $item_list);
      $this->parent->append_content($this->smarty->fetch('permission_tree.tpl'));
    }


    function show() {
      if (isset($_GET['actor_id']))
        $actor_id = $_GET['actor_id'] * 1;
      else
        die("PermissionTreePrinter::show(): Actor id missing");
      if (isset($_GET['resource_id']))
        $resource_id = $_GET['resource_id'] * 1;
      else
        $resource_id = NULL;
      $this->show_tree($actor_id, $resource_id);
    }
  }
?>
