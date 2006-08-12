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

function phpgacl_get_user_list($gacl_api, $group_id)
{
  $aro_table       = $gacl_api->_db_table_prefix . 'aro';
  $group_map_table = $gacl_api->_db_table_prefix . 'groups_aro_map';
  $query = '
    SELECT		a.id, a.name, a.value
    FROM		  '. $aro_table       .' a
    LEFT JOIN	'. $group_map_table .' b ON b.aro_id=a.id
    WHERE     b.group_id='. $group_id*1 .'
    AND       a.section_value="users"
    GROUP BY	a.id,a.name,a.value
    ORDER BY  a.name';
  $rs = &$gacl_api->db->Execute($query);
  //echo $query;
  $user_data = array();
  
  if(is_object($rs)) {
    while($row = $rs->FetchRow()) {
      $user_data[$row[0]] = array(
        'name' => $row[1],
        'value' => $row[2]
      );
    }
  }
  
  return $user_data;
}

function phpgacl_get_group_permission_list($gacl, $group_id, $section, $action)
{
  //echo "Group ID: $group_id, Section: $section, Action: $action<br>";
  $acl_table            = $gacl->_db_table_prefix . 'acl';
  $aco_map_table        = $gacl->_db_table_prefix . 'aco_map';
  $aro_groups_map_table = $gacl->_db_table_prefix . 'aro_groups_map';
  $axo_groups_map_table = $gacl->_db_table_prefix . 'axo_groups_map';
  $axo_groups_table     = $gacl->_db_table_prefix . 'axo_groups';
  $query = '
    SELECT    ag.id, ag.name, a.allow
    FROM      '. $acl_table            .' a
    LEFT JOIN '. $aco_map_table        .' ac  ON ac.acl_id=a.id
    LEFT JOIN '. $aro_groups_map_table .' arg ON arg.acl_id=a.id
    LEFT JOIN '. $axo_groups_map_table .' axg ON axg.acl_id=a.id
    LEFT JOIN '. $axo_groups_table     .' ag  ON ag.id=axg.group_id
    WHERE     a.enabled=1
    AND       ac.section_value="' . $section  . '"
    AND       ac.value="'         . $action   . '"
    AND       arg.group_id="'     . $group_id . '"
    ORDER BY  a.updated_DATE DESC';
  //$gacl->_debug = 1; $gacl->db->debug = 1;
  $rs = &$gacl->db->Execute($query);
  $user_data = array();
  
  if (is_object($rs)) {
    while($row = $rs->FetchRow()) {
      if ($row[2] == 1)
        $user_data['allow'][$row[0]] = $row[1];
      else
        $user_data['deny'][$row[0]]  = $row[1];
    }
  }
  //print_r($user_data);echo "<br>";
  return $user_data;
}

function phpgacl_get_user_permission_list($gacl, $user_id, $section, $action)
{
  //echo "Group ID: $group_id, Section: $section, Action: $action<br>";
  $acl_table            = $gacl->_db_table_prefix . 'acl';
  $aco_map_table        = $gacl->_db_table_prefix . 'aco_map';
  $aro_map_table        = $gacl->_db_table_prefix . 'aro_map';
  $aro_table            = $gacl->_db_table_prefix . 'aro';
  $axo_groups_map_table = $gacl->_db_table_prefix . 'axo_groups_map';
  $axo_groups_table     = $gacl->_db_table_prefix . 'axo_groups';
  $query = '
    SELECT    ag.id, ag.name, a.allow
    FROM      '. $acl_table            .' a
    LEFT JOIN '. $aco_map_table        .' acm  ON  acm.acl_id=a.id
    LEFT JOIN '. $aro_map_table        .' arm  ON  arm.acl_id=a.id
    LEFT JOIN '. $aro_table            .' ar   ON  ar.section_value=arm.section_value
                                               AND ar.value=arm.value
    LEFT JOIN '. $axo_groups_map_table .' axgm ON  axgm.acl_id=a.id
    LEFT JOIN '. $axo_groups_table     .' ag   ON  ag.id=axgm.group_id
    WHERE     a.enabled=1
    AND       acm.section_value="' . $section  . '"
    AND       acm.value="'         . $action   . '"
    AND       ar.id="'             . $user_id  . '"
    ORDER BY  a.updated_DATE DESC';
  //$gacl->_debug = 1; $gacl->db->debug = 1;
  $rs = &$gacl->db->Execute($query);
  $user_data = array();
  
  if (is_object($rs)) {
    while($row = $rs->FetchRow()) {
      if ($row[2] == 1)
        $user_data['allow'][$row[0]] = $row[1];
      else
        $user_data['deny'][$row[0]]  = $row[1];
    }
  }
  //print_r($user_data);echo "<br>";
  return $user_data;
}
