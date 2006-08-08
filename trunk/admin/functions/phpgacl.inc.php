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

function phpgacl_get_group_info($gacl_api, $group_id)
{
  $group_table  = $gacl_api->_db_table_prefix . 'aro_groups';
  $attrib_table = $gacl_api->_db_table_prefix . 'aro_groups_attribs';
  $query = '
    SELECT a.id, a.name, a.value, at.use_group_rights, at.description
    FROM      '. $group_table     .' a
    LEFT JOIN '. $attrib_table    .' at ON a.id=at.aro_id
    WHERE     a.id='. $group_id*1 .'
    ORDER BY  a.name
    LIMIT     1';
  //$gacl_api->db->debug = 1;
  $rs = &$gacl_api->db->Execute($query);
  //echo $query;

  $row = $rs->FetchRow();
  $group_data = array(
    'id'               => $row[0],
    'name'             => $row[1],
    'value'            => $row[2],
    'use_group_rights' => $row[3],
    'description'      => $row[4]
  );
  
  return $group_data;
}
?>
