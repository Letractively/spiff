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
function phpgacl_get_group_list($gacl_api, $parentid)
{
  $group_table     = $gacl_api->_db_table_prefix . 'aro_groups';
  $group_map_table = $gacl_api->_db_table_prefix . 'groups_aro_map';
  $query = '
    SELECT		a.id, a.name, a.value, count(b.aro_id)
    FROM		  '. $group_table     .' a
    LEFT JOIN	'. $group_map_table .' b ON b.group_id=a.id
    WHERE     a.parent_id='. $parentid*1 .'
    GROUP BY	a.id,a.name,a.value';
  $rs = &$gacl_api->db->Execute($query);
  //echo $query;
  $group_data = array();
  
  if(is_object($rs)) {
    while($row = $rs->FetchRow()) {
      $group_data[$row[0]] = array(
        'name' => $row[1],
        'value' => $row[2],
        'count' => $row[3]
      );
    }
  }
  
  return $group_data;
}

  class UserManagerPrinter extends PrinterBase {
    function show() {
      if (isset($_GET['gid']))
        $gid = $_GET['gid'] * 1;
      else
        $gid = $this->gacl->get_group_id('everybody');

      $groups = phpgacl_get_group_list($this->gacl, $gid);
      $this->smarty->clear_all_assign();
      $this->smarty->assign_by_ref('groups', $groups);
      //$this->smarty->assign_by_ref('users',  $users);
      $this->parent->append_content($this->smarty->fetch('usermanager.tpl'));
    }
  }
?>
