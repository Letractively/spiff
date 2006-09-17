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
        $resource = new SpiffAclActorGroup('');
        $resource->set_id(-1);
        break;

      case -2:
        // New user.
        $resource = new SpiffAclActor('');
        $resource->set_id(-2);
        break;

      default:
        // Existing user or group.
        $resource = $this->acldb->get_resource_from_id($id);
        assert('is_object($resource)');
        if (!$resource->is_group())
          $groups = $this->acldb->get_resource_parents($resource);
        else {
          $groups = $this->acldb->get_resource_children($resource,
                                                        NULL,
                                                        SPIFF_ACLDB_FETCH_GROUPS);
          $users  = $this->acldb->get_resource_children($resource,
                                                        NULL,
                                                        SPIFF_ACLDB_FETCH_ITEMS);
        }
        break;
      }

      $this->smarty->assign_by_ref('groups',    $groups);
      $this->smarty->assign_by_ref('users',     $users);
      $this->smarty->assign_by_ref('parent_id', $parent_id);
      if ($resource->is_group()) {
        $this->smarty->assign_by_ref('group', $resource);
        return $this->smarty->fetch('group_editor.tpl');
      }
      else {
        $this->smarty->assign_by_ref('user', $resource);
        return $this->smarty->fetch('user_editor.tpl');
      }
    }


    function delete_resource($id, $parent_id) {
      $this->acldb->delete_resource_from_id($id);
      return $this->show_resource($parent_id, $parent_id);
    }


    function add_group($parent_id) {
      return $this->show_resource(-1, $parent_id);
    }


    function add_user($parent_id) {
      return $this->show_resource(-2, $parent_id);
    }


    function submit_resource($id, $parent_id) {
      switch ($id) {
      case -1:
        // New group.
        $resource = new SpiffAclActorGroup($_POST['name']);
        break;

      case -2:
        // New user.
        $resource = new SpiffAclActor($_POST['name']);
        break;

      default:
        // Existing user or group.
        $resource = $this->acldb->get_resource_from_id($id);
        $resource->set_name($_POST['name']);
      }

      $resource->set_attribute('description',      $_POST['description']);
      $resource->set_attribute('use_group_rights', $_POST['use_group_rights'] ? TRUE : FALSE);

      $section = new SpiffAclResourceSection('users');
      if ($id == -1 || $id == -2)
        $resource = $this->acldb->add_resource($parent_id, $resource, $section);
      else
        $this->acldb->save_resource($resource, $section);

      // Save permissions.
      if (!isset($_POST['changelog_entries']))
        $_POST['changelog_entries'] = array();

      //print_r($_POST);
      foreach ($_POST['changelog_entries'] as $entry_name) {
        // Extract group id, user id and action name from the name.
        //echo "NAME: $entry_name<br>";
        if (!preg_match('/^changelog_input_(\d*)_users_([\w]+)_(\d*)$/',
                        $entry_name,
                        $matches))
          die("UserManagerPrinter::submit_resource(): invalid variable");
        $resource_id   = (int)$matches[1];
        $action_handle = $matches[2];
        $action_id     = (int)$matches[3];

        // Fetch the log entry details.
        //if (!isset($_POST[$entry_name . '_action']))
        //  die("UserManagerPrinter::submit_resource(): missing changelog e 1");
        //$action_name = $_POST[$entry_name . '_action'];
        if (!isset($_POST[$entry_name . '_permit']))
          die("UserManagerPrinter::submit_group(): missing changelog e 1");
        $permit = $_POST[$entry_name . '_permit'] * 1;

        // Build our objects.
        if ($action_id > 0)
          $action = $this->acldb->get_action_from_id($action_id);
        else
          $action  = $this->acldb->get_action_from_handle($action_handle,
                                                          'users');
        if ($resource_id)
          $resource = $this->acldb->get_resource_from_id($resource_id);

        // Push the new rule into the database.
        switch ($permit) {
        case -1:
          $this->acldb->unset_from_id((int)$id,
                                      $action->get_id(),
                                      $resource_id);
          break;

        case 1:
          $this->acldb->grant_from_id((int)$id,
                                      $action->get_id(),
                                      $resource_id);
          break;

        default:
          $this->acldb->deny_from_id((int)$id,
                                     $action->get_id(),
                                     $resource_id);
          break;
        }
      }

      return $resource->get_id();
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
        $resource  = $this->acldb->get_resource_from_handle('everybody',
                                                            'users');
        $id        = $resource->get_id();
        $parent_id = $id;
      }

      assert('is_int($id)');

      //echo "ID: $id, Parent ID: $parent_id<br>\n";
      if (isset($_POST['save'])) {
        $id = $this->submit_resource($id, $parent_id);
        return $this->show_resource($id, $parent_id);
      }
      elseif (isset($_POST['delete']))
        return $this->delete_resource($id, $parent_id);
      elseif (isset($_POST['group_add']))
        return $this->add_group($id);
      elseif (isset($_POST['user_add']))
        return $this->add_user($id);
      else
        return $this->show_resource($id, $parent_id);
    }
  }
?>
