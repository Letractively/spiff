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
  class UserManagerPrinter extends PrinterBase {
    public function show_resource($id, $parent_id) {
      switch ($id) {
      case -1:
        // New group.
        $section  = new SpiffAclResourceSection('users', '');
        $resource = new SpiffAclActorGroup('', '', $section);
        break;

      case -2:
        // New user.
        $section  = new SpiffAclResourceSection('users', '');
        $resource = new SpiffAclActor('', '', $section);
        break;

      default:
        // Existing user or group.
        $resource = $this->acldb->get_resource_from_id($id);
        $groups   = $this->acldb->get_resource_children($resource,
                                                        SPIFF_ACLDB_FETCH_GROUPS);
        $users    = $this->acldb->get_resource_children($resource,
                                                        SPIFF_ACLDB_FETCH_ITEMS);
        break;
      }

      $this->smarty->clear_all_assign();
      $this->smarty->assign_by_ref('groups',    $groups);
      $this->smarty->assign_by_ref('users',     $users);
      $this->smarty->assign_by_ref('parent_id', $parent_id);
      if ($resource->is_group()) {
        $this->smarty->assign_by_ref('group', $resource);
        $content = $this->smarty->fetch('group_editor.tpl');
      }
      else {
        $this->smarty->assign_by_ref('user', $resource);
        $content = $this->smarty->fetch('user_editor.tpl');
      }
      $this->parent->append_content($content);
    }


    function delete_resource($id, $parent_id) {
      $this->acldb->delete_resource_from_id($id);
      $this->show_resource($parent_id, $parent_id);
    }


    function add_group($parent_id) {
      $this->show_resource(-1, $parent_id);
    }


    function add_user($parent_id) {
      $this->show_resource(-2, $parent_id);
    }


    function submit_resource($id, $parent_id) {
      switch ($id) {
      case -1:
        // New group.
        $section  = new SpiffAclResourceSection('users', '');
        $resource = new SpiffAclActorGroup('', '', $section);
        $parent   = $this->acldb->get_resource_from_id($parent_id);
        break;

      case -2:
        // New user.
        $section  = new SpiffAclResourceSection('users', '');
        $resource = new SpiffAclActor('', '', $section);
        $parent   = $this->acldb->get_resource_from_id($parent_id);
        break;

      default:
        // Existing user or group.
        $resource = $this->acldb->get_resource_from_id($id);
      }

      $resource->set_name($_POST['name']);
      $resource->set_attribute('description',      $_POST['description']);
      $resource->set_attribute('use_group_rights', $_POST['use_group_rights'] ? TRUE : FALSE);

      if ($id == -1 || $id == -2)
        $resource = $this->acldb->add_resource($parent, $resource);
      else
        $this->acldb->save_resource($resource);

      // Save permissions.
      foreach ($_POST['changelog_entries'] as $entry_name) {
        // Extract group id, user id and action name from the name.
        echo "NAME: $entry_name<br>";
        if (!preg_match('/^changelog_input_(\d*)_(\w+)_(\d+)$/',
                        $entry_name,
                        $matches))
          die("UserManagerPrinter::submit_group(): invalid variable");
        $resource_id = $matches[1];

        // Fetch the log entry details.
        if (!isset($_POST[$entry_name . '_action']))
          die("UserManagerPrinter::submit_group(): missing changelog entry 1");
        $action_name = $_POST[$entry_name . '_action'];
        if (!isset($_POST[$entry_name . '_permit']))
          die("UserManagerPrinter::submit_group(): missing changelog entry 2");
        $permit = $_POST[$entry_name . '_permit'] * 1;

        // Build our objects.
        $section   = new GaclActionSection("Users");
        $action_id = $this->acldb->get_action_id_from_name($action_name,
                                                          $section);
        $action    = $this->acldb->get_action($action_id);
        if ($resource_id)
          $resource = $this->acldb->get_resource($resource_id);
        if ($resource_gid)
          $resource_group = $this->acldb->get_resource_group($resource_gid);

        // Push the new rule into the database.
        switch ($permit) {
        case -1:
          $this->acldb->kill(array($action),
                            array($group),
                            array($resource_group));
          break;

        case 1:
          $this->acldb->grant(array($action),
                             array($group),
                             array($resource_group));
          break;

        default:
          $this->acldb->deny(array($action),
                            array($group),
                            array($resource_group));
          break;
        }
      }
      print_r($_POST); //FIXME

      return $group->get_id();
    }


    function show() {
      // Get the parent id, if any.
      if (isset($_GET['parent_id']))
        $parent_id = (int)$_GET['parent_id'];
      else
        $parent_id = NULL;

      // Get the resource id. If none is given, fetch the "Everybody" group.
      if (isset($_GET['id']))
        $id = (int)$_GET['id'];
      else {
        $section   = new SpiffAclResourceSection('users', '');
        $resource  = $this->acldb->get_resource_from_handle('everybody',
                                                             $section);
        $id        = $resource->get_id();
        $parent_id = $id;
      }

      assert('isset($id)');

      if (isset($_POST['save'])) {
        $gid = $this->submit_resource($id, $parent_id);
        $this->show_resource($id, $parent_id);
      }
      elseif (isset($_POST['delete']))
        $this->delete_resource($id, $parent_id);
      elseif (isset($_POST['group_add']))
        $this->add_group($id);
      elseif (isset($_POST['user_add']))
        $this->add_user($id);
      else
        $this->show_resource($id, $parent_id);
    }
  }
?>
